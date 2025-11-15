-- Crew Copilot Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables (for development)
DROP TABLE IF EXISTS agent_execution_log CASCADE;
DROP TABLE IF EXISTS faa_compliance_log CASCADE;
DROP TABLE IF EXISTS claims CASCADE;
DROP TABLE IF EXISTS pay_calculations CASCADE;
DROP TABLE IF EXISTS flight_assignments CASCADE;
DROP TABLE IF EXISTS crew_members CASCADE;
DROP TABLE IF EXISTS pay_periods CASCADE;
DROP TABLE IF EXISTS premium_rules CASCADE;
DROP TABLE IF EXISTS per_diem_rates CASCADE;
DROP TABLE IF EXISTS faa_fdp_limits CASCADE;
DROP TABLE IF EXISTS contract_rules CASCADE;

-- Crew Members Table
CREATE TABLE crew_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    base_airport VARCHAR(3),  -- BUR, LAX, SFO
    role VARCHAR(50) NOT NULL,  -- Captain, First Officer, Flight Attendant
    seniority_date DATE,
    hire_date DATE NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    crew_type VARCHAR(20) NOT NULL,  -- line_holder, reserve
    monthly_guarantee DECIMAL(5,2),  -- hours
    contract_id UUID,
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, on_leave
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_crew_type CHECK (crew_type IN ('line_holder', 'reserve')),
    CONSTRAINT valid_role CHECK (role IN ('Captain', 'First Officer', 'Flight Attendant', 'Lead Flight Attendant'))
);

CREATE INDEX idx_crew_employee_id ON crew_members(employee_id);
CREATE INDEX idx_crew_base ON crew_members(base_airport);
CREATE INDEX idx_crew_role ON crew_members(role);

-- Flight Assignments Table
CREATE TABLE flight_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crew_member_id UUID REFERENCES crew_members(id) ON DELETE CASCADE,
    flight_number VARCHAR(20) NOT NULL,
    flight_date DATE NOT NULL,
    origin_airport VARCHAR(3) NOT NULL,
    destination_airport VARCHAR(3) NOT NULL,
    scheduled_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP,
    scheduled_block_time DECIMAL(5,2),  -- hours
    actual_block_time DECIMAL(5,2),  -- hours
    duty_report_time TIMESTAMP,
    duty_end_time TIMESTAMP,
    flight_duty_period DECIMAL(5,2),  -- hours
    aircraft_type VARCHAR(20),
    position VARCHAR(50),  -- captain, first_officer, flight_attendant_1, etc.
    overnight_location VARCHAR(3),  -- if layover
    is_international BOOLEAN DEFAULT FALSE,
    is_redeye BOOLEAN DEFAULT FALSE,
    is_deadhead BOOLEAN DEFAULT FALSE,
    trip_id VARCHAR(50),  -- groups multi-day pairings
    sequence_number INTEGER,  -- order in trip
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_flight_crew ON flight_assignments(crew_member_id);
CREATE INDEX idx_flight_date ON flight_assignments(flight_date);
CREATE INDEX idx_flight_number ON flight_assignments(flight_number);
CREATE INDEX idx_trip_id ON flight_assignments(trip_id);

-- Pay Calculations Table
CREATE TABLE pay_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crew_member_id UUID REFERENCES crew_members(id) ON DELETE CASCADE,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    flight_assignment_id UUID REFERENCES flight_assignments(id) ON DELETE SET NULL,
    calculation_type VARCHAR(50) NOT NULL,  -- flight_pay, per_diem, premium, guarantee
    base_hours DECIMAL(10,4),
    credit_hours DECIMAL(10,4),
    rate DECIMAL(10,2),
    amount DECIMAL(10,2) NOT NULL,
    calculation_details JSONB,  -- detailed breakdown
    calculated_by_agent VARCHAR(100),
    confidence_score DECIMAL(5,4) DEFAULT 1.0000,  -- 0.0000 to 1.0000
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_calculation_type CHECK (
        calculation_type IN ('flight_pay', 'per_diem', 'premium_overtime',
                            'premium_holiday', 'premium_redeye', 'premium_international',
                            'premium_training', 'guarantee', 'deadhead', 'cancellation')
    )
);

CREATE INDEX idx_pay_crew ON pay_calculations(crew_member_id);
CREATE INDEX idx_pay_period ON pay_calculations(pay_period_start, pay_period_end);
CREATE INDEX idx_pay_type ON pay_calculations(calculation_type);

-- Claims Table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    crew_member_id UUID REFERENCES crew_members(id) ON DELETE CASCADE,
    flight_assignment_id UUID REFERENCES flight_assignments(id) ON DELETE SET NULL,
    claim_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    amount_claimed DECIMAL(10,2),
    amount_approved DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'filed',  -- filed, investigating, approved, rejected, paid
    filed_via VARCHAR(20) DEFAULT 'system',  -- web, mobile, email, phone, system
    auto_detected BOOLEAN DEFAULT FALSE,
    agent_analysis JSONB,
    supporting_documents JSONB,
    assigned_to VARCHAR(100),
    resolution_notes TEXT,
    filed_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    resolved_at TIMESTAMP,
    paid_at TIMESTAMP,
    CONSTRAINT valid_claim_status CHECK (
        status IN ('filed', 'investigating', 'approved', 'rejected', 'paid', 'withdrawn')
    ),
    CONSTRAINT valid_claim_type CHECK (
        claim_type IN ('missing_flight_time', 'incorrect_block_time', 'missing_premium',
                      'per_diem_error', 'guarantee_not_applied', 'duty_violation', 'other')
    )
);

CREATE INDEX idx_claim_crew ON claims(crew_member_id);
CREATE INDEX idx_claim_status ON claims(status);
CREATE INDEX idx_claim_number ON claims(claim_number);

-- Agent Execution Log Table
CREATE TABLE agent_execution_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    execution_id UUID NOT NULL,  -- groups related agent calls
    crew_member_id UUID REFERENCES crew_members(id) ON DELETE SET NULL,
    input_data JSONB,
    output_data JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_name ON agent_execution_log(agent_name);
CREATE INDEX idx_execution_id ON agent_execution_log(execution_id);
CREATE INDEX idx_agent_created ON agent_execution_log(created_at);

-- FAA Compliance Log Table
CREATE TABLE faa_compliance_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crew_member_id UUID REFERENCES crew_members(id) ON DELETE CASCADE,
    flight_assignment_id UUID REFERENCES flight_assignments(id) ON DELETE SET NULL,
    regulation VARCHAR(50) NOT NULL,  -- Part 117.23, Part 121.471, etc.
    check_type VARCHAR(100) NOT NULL,  -- fdp_limit, rest_requirement, flight_time_limit
    is_compliant BOOLEAN NOT NULL,
    details JSONB,
    severity VARCHAR(20),  -- info, warning, violation
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_compliance_crew ON faa_compliance_log(crew_member_id);
CREATE INDEX idx_compliance_regulation ON faa_compliance_log(regulation);
CREATE INDEX idx_compliance_status ON faa_compliance_log(is_compliant);

-- Pay Periods Table
CREATE TABLE pay_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    year INTEGER NOT NULL,
    period_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'open',  -- open, closed, paid
    closed_at TIMESTAMP,
    paid_at TIMESTAMP,
    CONSTRAINT unique_period UNIQUE (year, period_number),
    CONSTRAINT valid_period_status CHECK (status IN ('open', 'closed', 'paid'))
);

CREATE INDEX idx_pay_period_dates ON pay_periods(period_start, period_end);

-- Premium Rules Table (Contract-based)
CREATE TABLE premium_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type VARCHAR(50) NOT NULL,  -- holiday, redeye, international, training, deadhead
    role VARCHAR(50),  -- Captain, First Officer, Flight Attendant (NULL = all)
    rate_type VARCHAR(20) NOT NULL,  -- multiplier, fixed_amount, percentage
    rate_value DECIMAL(10,2) NOT NULL,
    description TEXT,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_premium_type ON premium_rules(rule_type);
CREATE INDEX idx_premium_dates ON premium_rules(effective_date, expiration_date);

-- Per Diem Rates Table
CREATE TABLE per_diem_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(100) NOT NULL,
    state_country VARCHAR(100),  -- State for domestic, Country for international
    airport_code VARCHAR(3),
    rate DECIMAL(10,2) NOT NULL,
    is_international BOOLEAN DEFAULT FALSE,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    source VARCHAR(50),  -- GSA, State_Dept
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_perdiem_city ON per_diem_rates(city);
CREATE INDEX idx_perdiem_airport ON per_diem_rates(airport_code);
CREATE INDEX idx_perdiem_dates ON per_diem_rates(effective_date, expiration_date);

-- FAA Part 117 FDP Limits Table (Table B)
CREATE TABLE faa_fdp_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time_begin TIME NOT NULL,  -- Start of time window (e.g., 00:00)
    start_time_end TIME NOT NULL,    -- End of time window (e.g., 00:59)
    segments_1 DECIMAL(4,2),  -- Max FDP hours for 1 segment
    segments_2 DECIMAL(4,2),  -- Max FDP hours for 2 segments
    segments_3 DECIMAL(4,2),  -- Max FDP hours for 3 segments
    segments_4 DECIMAL(4,2),  -- Max FDP hours for 4 segments
    segments_5 DECIMAL(4,2),  -- Max FDP hours for 5 segments
    segments_6 DECIMAL(4,2),  -- Max FDP hours for 6 segments
    segments_7_plus DECIMAL(4,2)  -- Max FDP hours for 7+ segments
);

-- Contract Rules Table
CREATE TABLE contract_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_category VARCHAR(50) NOT NULL,  -- guarantee, overtime, scheduling
    rule_name VARCHAR(100) NOT NULL,
    role VARCHAR(50),  -- Captain, First Officer, Flight Attendant (NULL = all)
    crew_type VARCHAR(20),  -- line_holder, reserve (NULL = all)
    rule_value JSONB NOT NULL,  -- flexible storage for complex rules
    description TEXT,
    contract_reference VARCHAR(100),  -- e.g., "Section 12.3.A"
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contract_category ON contract_rules(rule_category);
CREATE INDEX idx_contract_role ON contract_rules(role);

-- Update triggers for timestamp columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_crew_members_updated_at BEFORE UPDATE ON crew_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flight_assignments_updated_at BEFORE UPDATE ON flight_assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE crew_members IS 'Stores crew member profiles and contract information';
COMMENT ON TABLE flight_assignments IS 'Individual flight assignments with actual vs scheduled times';
COMMENT ON TABLE pay_calculations IS 'All pay calculations broken down by type';
COMMENT ON TABLE claims IS 'Crew member pay claims and dispute resolution';
COMMENT ON TABLE agent_execution_log IS 'Audit trail for all AI agent executions';
COMMENT ON TABLE faa_compliance_log IS 'Compliance checks against FAA regulations';
COMMENT ON TABLE per_diem_rates IS 'GSA and State Department per diem rates by city';
COMMENT ON TABLE premium_rules IS 'Premium pay rules from union contracts';
COMMENT ON TABLE faa_fdp_limits IS 'FAA Part 117 Table B Flight Duty Period limits';
