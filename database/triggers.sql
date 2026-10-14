-- ==============================================================================
-- Project: City Bus Management System for Amravati
-- File: triggers.sql
-- Description: Business invariant enforcement and automated audit logging triggers.
-- Compatible with MySQL 8.x and MySQL Workbench.
-- ==============================================================================

USE city_bus_db;

DROP TRIGGER IF EXISTS trg_after_booking_insert_audit;
DROP TRIGGER IF EXISTS trg_after_booking_status_update;
DROP TRIGGER IF EXISTS trg_after_bus_status_change;

DELIMITER $$

-- ------------------------------------------------------------------------------
-- 1. Trigger: trg_after_booking_insert_audit
-- Automatically records an audit log row whenever a new booking is created.
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_after_booking_insert_audit
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        table_name,
        record_id,
        details,
        ip_address,
        created_at
    )
    VALUES (
        NEW.user_id,
        'INSERT_BOOKING',
        'bookings',
        NEW.booking_id,
        CONCAT('New booking created. Ref: ', NEW.booking_reference, ', Passengers: ', NEW.total_passengers, ', Amount: Rs.', NEW.total_amount),
        '127.0.0.1',
        NOW()
    );
END$$

-- ------------------------------------------------------------------------------
-- 2. Trigger: trg_after_booking_status_update
-- When a booking is marked 'cancelled', this trigger automatically synchronizes
-- child records: sets seat allocations in `booking_seats` to 'cancelled' and
-- sets ticket status in `tickets` to 'cancelled', plus logs the cancellation.
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_after_booking_status_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    -- Synchronize child status if booking is marked cancelled
    IF OLD.booking_status <> 'cancelled' AND NEW.booking_status = 'cancelled' THEN
        -- Mark seat allocations as cancelled so the seats immediately become available for other riders
        UPDATE booking_seats
        SET status = 'cancelled'
        WHERE booking_id = NEW.booking_id;

        -- Invalidate active ticket
        UPDATE tickets
        SET status = 'cancelled'
        WHERE booking_id = NEW.booking_id;

        -- Record cancellation event in audit trail
        INSERT INTO audit_logs (
            user_id,
            action,
            table_name,
            record_id,
            details,
            ip_address,
            created_at
        )
        VALUES (
            NEW.user_id,
            'CANCEL_BOOKING',
            'bookings',
            NEW.booking_id,
            CONCAT('Booking cancelled: ', NEW.booking_reference, '. Reason: ', COALESCE(NEW.cancellation_reason, 'No reason specified')),
            '127.0.0.1',
            NOW()
        );
    END IF;
END$$

-- ------------------------------------------------------------------------------
-- 3. Trigger: trg_after_bus_status_change
-- Audit tracks fleet status changes (e.g. moving a bus from 'active' to 'maintenance')
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_after_bus_status_change
AFTER UPDATE ON buses
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO audit_logs (
            user_id,
            action,
            table_name,
            record_id,
            details,
            ip_address,
            created_at
        )
        VALUES (
            NULL,
            'BUS_STATUS_CHANGED',
            'buses',
            NEW.bus_id,
            CONCAT('Bus ', NEW.bus_number, ' (Reg: ', NEW.registration_number, ') changed status from [', OLD.status, '] to [', NEW.status, ']'),
            '127.0.0.1',
            NOW()
        );
    END IF;
END$$

DELIMITER ;

-- ==============================================================================
-- TRIGGER TEST AND VERIFICATION QUERIES (Run manually in Workbench to test)
-- ==============================================================================
-- 1. Test bus status trigger:
-- UPDATE buses SET status = 'maintenance' WHERE bus_id = 1;
-- SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 1;
-- (Remember to revert back to active: UPDATE buses SET status = 'active' WHERE bus_id = 1;)

-- 2. Test booking cancellation sync trigger:
-- UPDATE bookings SET booking_status = 'cancelled', cancellation_reason = 'Lab Test Cancellation' WHERE booking_id = 2;
-- SELECT status FROM booking_seats WHERE booking_id = 2; -- Verify status is 'cancelled'
-- SELECT status FROM tickets WHERE booking_id = 2;       -- Verify ticket status is 'cancelled'
-- SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 1;
