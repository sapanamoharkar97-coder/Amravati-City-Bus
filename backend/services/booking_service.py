import time
import uuid
import datetime
from db import get_db_cursor
from services.fare_service import FareService

class BookingService:
    @staticmethod
    def create_booking(user_id: int, schedule_id: int, source_stop_id: int, 
                       dest_stop_id: int, seats: list, payment_method: str = "DEMO_UPI") -> dict:
        """
        Executes a database transaction with row-level locking (SELECT ... FOR UPDATE)
        to prevent race conditions and duplicate seat reservations.
        Guarantees Atomicity, Consistency, Isolation, and Durability (ACID).
        """
        if not seats or not isinstance(seats, list):
            raise ValueError("At least one seat must be selected for booking.")

        # Ensure unique requested seats within the same request
        requested_seat_numbers = [int(s['seat_number']) for s in seats]
        if len(requested_seat_numbers) != len(set(requested_seat_numbers)):
            raise ValueError("Duplicate seat numbers requested in the same booking.")

        with get_db_cursor(commit=True) as (conn, cursor):
            # 1. PESSIMISTIC ROW-LEVEL LOCK ON SCHEDULE AND BUS CAPACITY
            cursor.execute("""
                SELECT s.schedule_id, s.route_id, s.bus_id, s.journey_date, 
                       s.fare, s.status AS schedule_status, b.capacity, b.bus_number
                FROM schedules s
                INNER JOIN buses b ON s.bus_id = b.bus_id
                WHERE s.schedule_id = %s
                FOR UPDATE;
            """, (schedule_id,))
            schedule = cursor.fetchone()

            if not schedule:
                raise ValueError("Bus schedule not found.")

            status = schedule.get('schedule_status') if isinstance(schedule, dict) else schedule[5]
            if status != 'scheduled':
                raise ValueError(f"Cannot book seats. Bus schedule status is currently '{status}'.")

            bus_capacity = schedule.get('capacity') if isinstance(schedule, dict) else schedule[6]
            route_id = schedule.get('route_id') if isinstance(schedule, dict) else schedule[1]
            journey_date = schedule.get('journey_date') if isinstance(schedule, dict) else schedule[3]

            # Validate seat numbers are within physical bus capacity
            for seat_num in requested_seat_numbers:
                if seat_num < 1 or seat_num > bus_capacity:
                    raise ValueError(f"Seat #{seat_num} is invalid for this bus (Capacity: {bus_capacity}).")

            # 2. CHECK EXISTING BOOKED SEATS WITH LOCKING
            format_strings = ','.join(['%s'] * len(requested_seat_numbers))
            cursor.execute(f"""
                SELECT seat_number 
                FROM booking_seats 
                WHERE schedule_id = %s 
                  AND status = 'booked' 
                  AND seat_number IN ({format_strings})
                FOR UPDATE;
            """, [schedule_id] + requested_seat_numbers)
            already_booked = cursor.fetchall()

            if already_booked:
                booked_nums = [str(r.get('seat_number') if isinstance(r, dict) else r[0]) for r in already_booked]
                raise ValueError(f"Seat(s) already booked by another passenger: {', '.join(booked_nums)}.")

            # 3. CALCULATE STAGE FARE
            fare_info = FareService.calculate_fare(route_id, source_stop_id, dest_stop_id)
            unit_fare = fare_info['fare_per_passenger']
            total_passengers = len(seats)
            total_amount = unit_fare * total_passengers

            # 4. GENERATE UNIQUE BOOKING REFERENCE
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d")
            random_suffix = uuid.uuid4().hex[:6].upper()
            booking_ref = f"AMT-BK-{timestamp_str}-{random_suffix}"

            # 5. INSERT MASTER BOOKING
            cursor.execute("""
                INSERT INTO bookings (
                    booking_reference, user_id, schedule_id, source_stop_id, 
                    destination_stop_id, journey_date, total_passengers, 
                    total_amount, booking_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'confirmed');
            """, (
                booking_ref, user_id, schedule_id, source_stop_id,
                dest_stop_id, journey_date, total_passengers, total_amount
            ))
            booking_id = cursor.lastrowid

            # 6. INSERT INDIVIDUAL PASSENGER SEAT ALLOCATIONS
            for s in seats:
                seat_num = int(s['seat_number'])
                p_name = s.get('passenger_name', '').strip() or 'Passenger'
                p_age = int(s.get('passenger_age', 25))
                p_gender = s.get('passenger_gender', 'other').lower()
                if p_gender not in ('male', 'female', 'other'):
                    p_gender = 'other'

                cursor.execute("""
                    INSERT INTO booking_seats (
                        booking_id, schedule_id, seat_number, passenger_name, 
                        passenger_age, passenger_gender, fare, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'booked');
                """, (
                    booking_id, schedule_id, seat_num, p_name, p_age, p_gender, unit_fare
                ))

            # 7. GENERATE TICKET ARTIFACT WITH QR DATA
            ticket_number = f"TKT-AMT-{schedule_id}-{booking_id}-{uuid.uuid4().hex[:4].upper()}"
            qr_payload = f"AMT-SECURE-TKT:{ticket_number}:BK:{booking_ref}:SEATS:{','.join(map(str, requested_seat_numbers))}"
            cursor.execute("""
                INSERT INTO tickets (ticket_number, booking_id, qr_code_data, status)
                VALUES (%s, %s, %s, 'valid');
            """, (ticket_number, booking_id, qr_payload))

            # 8. INSERT DEMONSTRATION PAYMENT RECORD
            payment_ref = f"PAY-DEMO-{int(time.time())}-{uuid.uuid4().hex[:4].upper()}"
            cursor.execute("""
                INSERT INTO payments (
                    payment_reference, booking_id, amount, payment_method, 
                    transaction_status, notes
                ) VALUES (%s, %s, %s, %s, 'success', 'Academic Demonstration Payment Authorized');
            """, (payment_ref, booking_id, total_amount, payment_method))

            return {
                "booking_id": booking_id,
                "booking_reference": booking_ref,
                "ticket_number": ticket_number,
                "payment_reference": payment_ref,
                "journey_date": str(journey_date),
                "total_passengers": total_passengers,
                "total_amount": total_amount,
                "unit_fare": unit_fare,
                "booked_seats": requested_seat_numbers
            }

    @staticmethod
    def cancel_booking(booking_id: int, user_id: int = None, is_admin: bool = False, reason: str = "Passenger Cancellation") -> dict:
        """
        Cancels an existing booking, frees the reserved seats for other riders,
        and marks related ticket and payment records as cancelled/refunded.
        """
        with get_db_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                SELECT booking_id, booking_reference, user_id, booking_status, journey_date
                FROM bookings
                WHERE booking_id = %s
                FOR UPDATE;
            """, (booking_id,))
            booking = cursor.fetchone()

            if not booking:
                raise ValueError("Booking not found.")

            b_user_id = booking.get('user_id') if isinstance(booking, dict) else booking[2]
            b_status = booking.get('booking_status') if isinstance(booking, dict) else booking[3]

            if not is_admin and user_id is not None and b_user_id != user_id:
                raise PermissionError("You are not authorized to cancel this booking.")

            if b_status == 'cancelled':
                raise ValueError("This booking is already cancelled.")

            # Update booking status
            cursor.execute("""
                UPDATE bookings
                SET booking_status = 'cancelled',
                    cancellation_reason = %s,
                    cancelled_at = NOW()
                WHERE booking_id = %s;
            """, (reason, booking_id))

            # Release reserved seats
            cursor.execute("""
                UPDATE booking_seats
                SET status = 'cancelled'
                WHERE booking_id = %s;
            """, (booking_id,))

            # Invalidate ticket
            cursor.execute("""
                UPDATE tickets
                SET status = 'cancelled'
                WHERE booking_id = %s;
            """, (booking_id,))

            # Mark payment as refunded in demo ledger
            cursor.execute("""
                UPDATE payments
                SET transaction_status = 'refunded',
                    notes = 'Demo Refund Credited Following Cancellation'
                WHERE booking_id = %s;
            """, (booking_id,))

            return {
                "booking_id": booking_id,
                "status": "cancelled",
                "message": "Booking has been successfully cancelled and seats released."
            }
