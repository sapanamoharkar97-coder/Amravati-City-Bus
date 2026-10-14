import logging
from db import get_db_cursor

logger = logging.getLogger(__name__)

class FareService:
    @staticmethod
    def calculate_fare(route_id: int, source_stop_id: int, dest_stop_id: int) -> dict:
        """
        Calculates the per-passenger fare between two stops on a given route
        based on route base fare and intermediate stop stage fares.
        """
        with get_db_cursor(commit=False) as (conn, cursor):
            # Fetch route base fare
            cursor.execute("SELECT base_fare FROM bus_routes WHERE route_id = %s;", (route_id,))
            route = cursor.fetchone()
            if not route:
                raise ValueError("Specified bus route does not exist.")
            base_fare = float(route.get('base_fare', 10.00) if isinstance(route, dict) else route[0])

            # Fetch source stop sequence and fare stage
            cursor.execute("""
                SELECT stop_sequence, fare_from_source, distance_from_source_km 
                FROM route_stops 
                WHERE route_id = %s AND stop_id = %s;
            """, (route_id, source_stop_id))
            src_stop = cursor.fetchone()

            # Fetch destination stop sequence and fare stage
            cursor.execute("""
                SELECT stop_sequence, fare_from_source, distance_from_source_km 
                FROM route_stops 
                WHERE route_id = %s AND stop_id = %s;
            """, (route_id, dest_stop_id))
            dst_stop = cursor.fetchone()

            if not src_stop or not dst_stop:
                raise ValueError("Selected stops do not belong to the route sequence.")

            src_seq = src_stop.get('stop_sequence') if isinstance(src_stop, dict) else src_stop[0]
            dst_seq = dst_stop.get('stop_sequence') if isinstance(dst_stop, dict) else dst_stop[0]

            if src_seq >= dst_seq:
                raise ValueError("Boarding stop must precede the destination stop in travel direction.")

            src_fare_stage = float(src_stop.get('fare_from_source') if isinstance(src_stop, dict) else src_stop[1])
            dst_fare_stage = float(dst_stop.get('fare_from_source') if isinstance(dst_stop, dict) else dst_stop[1])

            calculated_fare = abs(dst_fare_stage - src_fare_stage)
            final_fare = max(base_fare, calculated_fare)

            src_dist = float(src_stop.get('distance_from_source_km') if isinstance(src_stop, dict) else src_stop[2])
            dst_dist = float(dst_stop.get('distance_from_source_km') if isinstance(dst_stop, dict) else dst_stop[2])
            journey_distance = abs(dst_dist - src_dist)

            return {
                "route_id": route_id,
                "fare_per_passenger": final_fare,
                "journey_distance_km": journey_distance,
                "boarding_sequence": src_seq,
                "destination_sequence": dst_seq
            }
