-- FAA Part 117 Table B - Flight Duty Period Limits
-- Based on acclimation time and number of flight segments

INSERT INTO faa_fdp_limits (start_time_begin, start_time_end, segments_1, segments_2, segments_3, segments_4, segments_5, segments_6, segments_7_plus) VALUES
('00:00:00', '00:59:00', 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00),
('01:00:00', '01:59:00', 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00),
('02:00:00', '02:59:00', 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00),
('03:00:00', '03:59:00', 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00),
('04:00:00', '04:59:00', 10.00, 10.00, 10.00, 10.00, 9.00, 9.00, 9.00),
('05:00:00', '05:59:00', 12.00, 12.00, 12.00, 12.00, 11.50, 11.00, 10.50),
('06:00:00', '06:59:00', 13.00, 13.00, 12.00, 12.00, 11.50, 11.00, 10.50),
('07:00:00', '12:59:00', 14.00, 14.00, 13.00, 13.00, 12.50, 12.00, 11.50),
('13:00:00', '16:59:00', 13.00, 13.00, 12.00, 12.00, 11.50, 11.00, 10.50),
('17:00:00', '21:59:00', 12.00, 12.00, 12.00, 12.00, 11.50, 11.00, 10.50),
('22:00:00', '22:59:00', 11.00, 11.00, 11.00, 11.00, 10.00, 9.00, 9.00),
('23:00:00', '23:59:00', 10.00, 10.00, 10.00, 10.00, 9.00, 9.00, 9.00);

-- Premium Pay Rules (based on typical union contracts)
INSERT INTO premium_rules (rule_type, role, rate_type, rate_value, description, effective_date) VALUES
-- Holiday Pay
('holiday', NULL, 'multiplier', 1.5, 'Holiday pay at 1.5x hourly rate for designated holidays', '2025-01-01'),

-- Red-Eye Premium
('redeye', 'Captain', 'fixed_amount', 100.00, 'Red-eye premium for flights departing 2200-0559', '2025-01-01'),
('redeye', 'First Officer', 'fixed_amount', 75.00, 'Red-eye premium for flights departing 2200-0559', '2025-01-01'),
('redeye', 'Flight Attendant', 'fixed_amount', 50.00, 'Red-eye premium for flights departing 2200-0559', '2025-01-01'),

-- International Premium
('international', NULL, 'percentage', 15.00, 'International premium 15% of base pay', '2025-01-01'),

-- Deadhead Pay
('deadhead', NULL, 'percentage', 50.00, 'Deadhead positioning flights at 50% of hourly rate', '2025-01-01'),

-- Training Pay
('training', 'Captain', 'fixed_amount', 125.00, 'Training/check ride pay per session', '2025-01-01'),
('training', 'First Officer', 'fixed_amount', 100.00, 'Training/check ride pay per session', '2025-01-01'),
('training', 'Flight Attendant', 'fixed_amount', 75.00, 'Training/recurrent pay per session', '2025-01-01'),

-- Cancellation Pay
('cancellation', NULL, 'percentage', 50.00, 'Cancellation pay at 50% of trip value', '2025-01-01');

-- Contract Guarantee Rules
INSERT INTO contract_rules (rule_category, rule_name, role, crew_type, rule_value, description, contract_reference, effective_date) VALUES
-- Monthly Guarantees
('guarantee', 'Monthly Minimum Line Holder', 'Captain', 'line_holder',
 '{"hours": 75, "type": "monthly"}',
 'Line holding captains guaranteed 75 hours per month', 'Section 8.A.1', '2025-01-01'),

('guarantee', 'Monthly Minimum Line Holder', 'First Officer', 'line_holder',
 '{"hours": 75, "type": "monthly"}',
 'Line holding first officers guaranteed 75 hours per month', 'Section 8.A.1', '2025-01-01'),

('guarantee', 'Monthly Minimum Line Holder', 'Flight Attendant', 'line_holder',
 '{"hours": 70, "type": "monthly"}',
 'Line holding flight attendants guaranteed 70 hours per month', 'Section 8.A.2', '2025-01-01'),

-- Reserve Guarantees
('guarantee', 'Monthly Minimum Reserve', 'Captain', 'reserve',
 '{"hours": 73, "type": "monthly"}',
 'Reserve captains guaranteed 73 hours per month', 'Section 8.B.1', '2025-01-01'),

('guarantee', 'Monthly Minimum Reserve', 'First Officer', 'reserve',
 '{"hours": 73, "type": "monthly"}',
 'Reserve first officers guaranteed 73 hours per month', 'Section 8.B.1', '2025-01-01'),

('guarantee', 'Monthly Minimum Reserve', 'Flight Attendant', 'reserve',
 '{"hours": 70, "type": "monthly"}',
 'Reserve flight attendants guaranteed 70 hours per month', 'Section 8.B.2', '2025-01-01'),

-- Daily Guarantees
('guarantee', 'Daily Minimum', NULL, NULL,
 '{"hours": 4.0, "type": "daily"}',
 'Minimum 4 hours pay per duty period', 'Section 8.C.1', '2025-01-01'),

-- Trip Guarantees
('guarantee', 'Trip Minimum', NULL, NULL,
 '{"min_credit_per_segment": 1.0}',
 'Minimum 1 hour credit per flight segment', 'Section 8.D.1', '2025-01-01');

-- Sample Per Diem Rates (GSA 2025)
INSERT INTO per_diem_rates (city, state_country, airport_code, rate, is_international, effective_date, source) VALUES
-- California Cities
('Burbank', 'California', 'BUR', 79.00, FALSE, '2025-01-01', 'GSA'),
('Los Angeles', 'California', 'LAX', 79.00, FALSE, '2025-01-01', 'GSA'),
('San Francisco', 'California', 'SFO', 84.00, FALSE, '2025-01-01', 'GSA'),
('San Diego', 'California', 'SAN', 79.00, FALSE, '2025-01-01', 'GSA'),
('San Jose', 'California', 'SJC', 84.00, FALSE, '2025-01-01', 'GSA'),

-- Oregon
('Portland', 'Oregon', 'PDX', 74.00, FALSE, '2025-01-01', 'GSA'),
('Eugene', 'Oregon', 'EUG', 64.00, FALSE, '2025-01-01', 'GSA'),

-- Washington
('Seattle', 'Washington', 'SEA', 79.00, FALSE, '2025-01-01', 'GSA'),

-- Nevada
('Las Vegas', 'Nevada', 'LAS', 74.00, FALSE, '2025-01-01', 'GSA'),
('Reno', 'Nevada', 'RNO', 64.00, FALSE, '2025-01-01', 'GSA'),

-- Arizona
('Phoenix', 'Arizona', 'PHX', 69.00, FALSE, '2025-01-01', 'GSA'),

-- Utah
('Salt Lake City', 'Utah', 'SLC', 69.00, FALSE, '2025-01-01', 'GSA'),
('Provo', 'Utah', 'PVU', 64.00, FALSE, '2025-01-01', 'GSA'),

-- Colorado
('Denver', 'Colorado', 'DEN', 74.00, FALSE, '2025-01-01', 'GSA'),

-- International (State Department rates)
('Cabo San Lucas', 'Mexico', 'SJD', 125.00, TRUE, '2025-01-01', 'State_Dept'),
('Puerto Vallarta', 'Mexico', 'PVR', 110.00, TRUE, '2025-01-01', 'State_Dept'),
('Cancun', 'Mexico', 'CUN', 115.00, TRUE, '2025-01-01', 'State_Dept');

-- Create current pay period
INSERT INTO pay_periods (period_start, period_end, year, period_number, status) VALUES
('2025-11-01', '2025-11-15', 2025, 21, 'open'),
('2025-11-16', '2025-11-30', 2025, 22, 'open');
