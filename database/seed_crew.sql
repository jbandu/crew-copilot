-- Seed Data: Test Crew Members for Avelo Airlines

-- Sample Crew Members (5 crew members for testing)
INSERT INTO crew_members (employee_id, first_name, last_name, email, phone, base_airport, role, seniority_date, hire_date, hourly_rate, crew_type, monthly_guarantee) VALUES
-- Captains
('P12345', 'Sarah', 'Chen', 'sarah.chen@aveloair.com', '555-0101', 'BUR', 'Captain', '2021-04-15', '2021-04-15', 105.00, 'line_holder', 75.00),
('P12346', 'Michael', 'Rodriguez', 'michael.rodriguez@aveloair.com', '555-0102', 'BUR', 'Captain', '2021-06-01', '2021-06-01', 105.00, 'reserve', 73.00),

-- First Officers
('P23456', 'Jessica', 'Williams', 'jessica.williams@aveloair.com', '555-0201', 'BUR', 'First Officer', '2021-08-10', '2021-08-10', 75.00, 'line_holder', 75.00),

-- Flight Attendants
('FA34567', 'David', 'Thompson', 'david.thompson@aveloair.com', '555-0301', 'BUR', 'Flight Attendant', '2021-05-20', '2021-05-20', 35.00, 'line_holder', 70.00),
('FA34568', 'Emily', 'Martinez', 'emily.martinez@aveloair.com', '555-0302', 'BUR', 'Lead Flight Attendant', '2021-04-20', '2021-04-20', 38.00, 'line_holder', 70.00);

-- Verify insert
SELECT
    employee_id,
    first_name,
    last_name,
    role,
    hourly_rate,
    crew_type,
    monthly_guarantee
FROM crew_members
ORDER BY role, employee_id;
