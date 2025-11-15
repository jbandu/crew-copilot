-- Seed Data: Sample Flight Assignments for Testing
-- Pay Period: 2025-11-01 to 2025-11-15

-- Get crew member IDs for reference
DO $$
DECLARE
    sarah_id UUID;
    michael_id UUID;
    jessica_id UUID;
    david_id UUID;
    emily_id UUID;
BEGIN
    -- Get crew member IDs
    SELECT id INTO sarah_id FROM crew_members WHERE employee_id = 'P12345';
    SELECT id INTO michael_id FROM crew_members WHERE employee_id = 'P12346';
    SELECT id INTO jessica_id FROM crew_members WHERE employee_id = 'P23456';
    SELECT id INTO david_id FROM crew_members WHERE employee_id = 'FA34567';
    SELECT id INTO emily_id FROM crew_members WHERE employee_id = 'FA34568';

    -- Trip 1: Sarah Chen (Captain) - BUR-PDX-BUR (Nov 3-4)
    -- Day 1: BUR to PDX (red-eye departure)
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, overnight_location, is_redeye, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP101', '2025-11-03', 'BUR', 'PDX',
     '2025-11-03 22:30:00', '2025-11-03 22:45:00',
     '2025-11-04 01:15:00', '2025-11-04 01:20:00',
     2.75, 2.58, '2025-11-03 21:30:00', '2025-11-04 02:00:00', 4.50,
     'B737-800', 'captain', 'PDX', TRUE, 'TRIP-001', 1);

    -- Day 2: PDX to BUR
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP102', '2025-11-04', 'PDX', 'BUR',
     '2025-11-04 15:00:00', '2025-11-04 15:10:00',
     '2025-11-04 17:45:00', '2025-11-04 17:55:00',
     2.75, 2.75, '2025-11-04 14:00:00', '2025-11-04 18:30:00', 4.50,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-001', 2);

    -- Trip 2: Sarah Chen - BUR-LAS-BUR (Nov 7)
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP201', '2025-11-07', 'BUR', 'LAS',
     '2025-11-07 08:00:00', '2025-11-07 08:05:00',
     '2025-11-07 09:15:00', '2025-11-07 09:10:00',
     1.25, 1.08, '2025-11-07 07:00:00', '2025-11-07 13:30:00', 6.50,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-002', 1);

    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP202', '2025-11-07', 'LAS', 'BUR',
     '2025-11-07 12:00:00', '2025-11-07 12:15:00',
     '2025-11-07 13:15:00', '2025-11-07 13:20:00',
     1.25, 1.08, '2025-11-07 07:00:00', '2025-11-07 13:30:00', 6.50,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-002', 2);

    -- Trip 3: Sarah Chen - BUR-SFO-BUR-SEA-BUR (Nov 10-11, includes holiday Nov 11 - Veterans Day)
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, overnight_location, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP301', '2025-11-10', 'BUR', 'SFO',
     '2025-11-10 06:00:00', '2025-11-10 06:05:00',
     '2025-11-10 07:30:00', '2025-11-10 07:35:00',
     1.50, 1.50, '2025-11-10 05:00:00', '2025-11-10 19:30:00', 14.50,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-003', 1);

    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, overnight_location, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP302', '2025-11-10', 'SFO', 'BUR',
     '2025-11-10 10:00:00', '2025-11-10 10:10:00',
     '2025-11-10 11:30:00', '2025-11-10 11:40:00',
     1.50, 1.50, '2025-11-10 05:00:00', '2025-11-10 19:30:00', 14.50,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-003', 2);

    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, overnight_location, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP303', '2025-11-10', 'BUR', 'SEA',
     '2025-11-10 16:00:00', '2025-11-10 16:15:00',
     '2025-11-10 18:45:00', '2025-11-10 18:50:00',
     2.75, 2.58, '2025-11-10 05:00:00', '2025-11-10 19:30:00', 14.50,
     'B737-800', 'captain', 'SEA', FALSE, 'TRIP-003', 3);

    -- Day 2 of Trip 3 - Veterans Day (Holiday)
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP304', '2025-11-11', 'SEA', 'BUR',
     '2025-11-11 14:00:00', '2025-11-11 14:05:00',
     '2025-11-11 16:30:00', '2025-11-11 16:35:00',
     2.50, 2.50, '2025-11-11 13:00:00', '2025-11-11 17:00:00', 4.00,
     'B737-800', 'captain', NULL, FALSE, 'TRIP-003', 4);

    -- Trip 4: Sarah Chen - BUR-SJD-BUR (Nov 14-15, red-eye return, international)
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, overnight_location, is_international, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP401', '2025-11-14', 'BUR', 'SJD',
     '2025-11-14 10:00:00', '2025-11-14 10:10:00',
     '2025-11-14 13:30:00', '2025-11-14 13:40:00',
     3.50, 3.50, '2025-11-14 09:00:00', '2025-11-15 03:00:00', 5.00,
     'B737-800', 'captain', 'SJD', TRUE, 'TRIP-004', 1);

    -- Red-eye return from Cabo
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, is_international, is_redeye, trip_id, sequence_number)
    VALUES
    (sarah_id, 'XP402', '2025-11-15', 'SJD', 'BUR',
     '2025-11-15 00:30:00', '2025-11-15 00:40:00',
     '2025-11-15 03:00:00', '2025-11-15 03:10:00',
     3.50, 3.50, '2025-11-14 23:30:00', '2025-11-15 04:00:00', 4.50,
     'B737-800', 'captain', NULL, TRUE, TRUE, 'TRIP-004', 2);

    -- Jessica Williams (First Officer) - Sample flights
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (jessica_id, 'XP501', '2025-11-05', 'BUR', 'PHX',
     '2025-11-05 07:00:00', '2025-11-05 07:05:00',
     '2025-11-05 08:30:00', '2025-11-05 08:35:00',
     1.50, 1.50, '2025-11-05 06:00:00', '2025-11-05 13:00:00', 7.00,
     'B737-800', 'first_officer', NULL, FALSE, 'TRIP-005', 1);

    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (jessica_id, 'XP502', '2025-11-05', 'PHX', 'BUR',
     '2025-11-05 11:00:00', '2025-11-05 11:10:00',
     '2025-11-05 12:30:00', '2025-11-05 12:40:00',
     1.50, 1.50, '2025-11-05 06:00:00', '2025-11-05 13:00:00', 7.00,
     'B737-800', 'first_officer', NULL, FALSE, 'TRIP-005', 2);

    -- David Thompson (Flight Attendant) - Sample flights
    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (david_id, 'XP601', '2025-11-06', 'BUR', 'SAN',
     '2025-11-06 09:00:00', '2025-11-06 09:05:00',
     '2025-11-06 10:00:00', '2025-11-06 10:05:00',
     1.00, 1.00, '2025-11-06 08:00:00', '2025-11-06 14:00:00', 6.00,
     'B737-800', 'flight_attendant_1', NULL, FALSE, 'TRIP-006', 1);

    INSERT INTO flight_assignments (crew_member_id, flight_number, flight_date, origin_airport, destination_airport,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
        scheduled_block_time, actual_block_time, duty_report_time, duty_end_time, flight_duty_period,
        aircraft_type, position, trip_id, sequence_number)
    VALUES
    (david_id, 'XP602', '2025-11-06', 'SAN', 'BUR',
     '2025-11-06 12:00:00', '2025-11-06 12:10:00',
     '2025-11-06 13:00:00', '2025-11-06 13:10:00',
     1.00, 1.00, '2025-11-06 08:00:00', '2025-11-06 14:00:00', 6.00,
     'B737-800', 'flight_attendant_1', NULL, FALSE, 'TRIP-006', 2);

END $$;

-- Verify inserted flights
SELECT
    cm.employee_id,
    cm.first_name,
    cm.last_name,
    fa.flight_number,
    fa.flight_date,
    fa.origin_airport,
    fa.destination_airport,
    fa.actual_block_time,
    fa.is_redeye,
    fa.is_international,
    fa.trip_id
FROM flight_assignments fa
JOIN crew_members cm ON fa.crew_member_id = cm.id
ORDER BY cm.employee_id, fa.flight_date, fa.trip_id, fa.sequence_number;

-- Summary by crew member
SELECT
    cm.employee_id,
    cm.first_name,
    cm.last_name,
    cm.role,
    COUNT(fa.id) as total_flights,
    SUM(fa.actual_block_time) as total_block_hours,
    COUNT(DISTINCT fa.trip_id) as total_trips
FROM crew_members cm
LEFT JOIN flight_assignments fa ON cm.id = fa.crew_member_id
    AND fa.flight_date BETWEEN '2025-11-01' AND '2025-11-15'
GROUP BY cm.employee_id, cm.first_name, cm.last_name, cm.role
ORDER BY cm.employee_id;
