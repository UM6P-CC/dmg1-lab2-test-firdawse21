import os
import pymysql
import pytest


# CONFIG
DB_NAME = "RLMS_LAB2"


@pytest.fixture(scope="session")
def connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        autocommit=True,
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database(connection):
    """Creates a fresh, empty RLMS_LAB2 once per session. Each Exercise
    below then creates ONE table into this same database using the
    student's own SQL -- later exercises rely on earlier ones having
    already created the tables they reference via FOREIGN KEY (same
    pattern as Lab 5's cumulative trigger tests). If you run a single
    exercise in isolation rather than the whole file, run the exercises
    it depends on first, or its FOREIGN KEY will fail with a real MySQL
    error naming the missing referenced table.
    """
    cur = connection.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    cur.close()
    yield


@pytest.fixture
def cursor(connection, setup_database):
    cur = connection.cursor()
    cur.execute(f"USE {DB_NAME}")
    yield cur
    cur.close()


# ============================================================================
# EXPECTED SCHEMA (private answer key)
# ============================================================================
try:
    from lab2_expected_schema import EXPECTED_SCHEMA
except ImportError as exc:
    raise ImportError(
        "lab2_expected_schema.py not found. This file holds the private "
        "expected relational schema for Lab 2 and is intentionally NOT "
        "included in the student-facing repository."
    ) from exc


# ============================================================================
# INFORMATION_SCHEMA introspection + grading helper
# ============================================================================

def _table_exists(cur, table_name):
    cur.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s)",
        (DB_NAME, table_name),
    )
    return cur.fetchone()[0] > 0


def _actual_columns(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s)",
        (DB_NAME, table_name),
    )
    return {row[0].lower() for row in cur.fetchall()}


def _actual_primary_key(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s) "
        "AND CONSTRAINT_NAME = 'PRIMARY'",
        (DB_NAME, table_name),
    )
    return {row[0].lower() for row in cur.fetchall()}


def _actual_foreign_keys(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
        "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s) "
        "AND REFERENCED_TABLE_NAME IS NOT NULL",
        (DB_NAME, table_name),
    )
    return {(col.lower(), ref_t.lower(), ref_c.lower()) for col, ref_t, ref_c in cur.fetchall()}


def assert_table_matches_expected(cursor, sql, table_name):
    """
    Runs the student's CREATE TABLE statement for `table_name`, then checks
    it against the private answer key via INFORMATION_SCHEMA: the table
    must exist, have exactly the expected columns (name match, case-
    insensitive), the expected primary key, and the expected foreign keys.
    Column data TYPES are intentionally not checked (graded flexibly per
    the course rubric -- e.g. VARCHAR(50) vs VARCHAR(120) are both fine).
    """
    cursor.execute(sql)

    expected = EXPECTED_SCHEMA[table_name]

    if not _table_exists(cursor, table_name):
        pytest.fail(
            f"No table named '{table_name}' was found after running your "
            f"SQL -- check your CREATE TABLE statement uses this exact "
            f"table name."
        )

    expected_columns = {c.lower() for c in expected["columns"]}
    actual_columns = _actual_columns(cursor, table_name)
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    expected_pk = {c.lower() for c in expected["primary_key"]}
    actual_pk = _actual_primary_key(cursor, table_name)

    expected_fks = {(c.lower(), t.lower(), r.lower()) for c, t, r in expected["foreign_keys"]}
    actual_fks = _actual_foreign_keys(cursor, table_name)
    missing_fks = expected_fks - actual_fks
    extra_fks = actual_fks - expected_fks

    problems = []
    if missing_columns:
        problems.append(f"missing column(s): {sorted(missing_columns)}")
    if extra_columns:
        problems.append(f"unexpected extra column(s): {sorted(extra_columns)}")
    if actual_pk != expected_pk:
        problems.append(
            f"primary key mismatch -- expected {sorted(expected_pk)}, "
            f"got {sorted(actual_pk)}"
        )
    if missing_fks:
        readable = [f"{c} -> {t}({r})" for c, t, r in sorted(missing_fks)]
        problems.append(f"missing foreign key(s): {readable}")
    if extra_fks:
        readable = [f"{c} -> {t}({r})" for c, t, r in sorted(extra_fks)]
        problems.append(f"unexpected foreign key(s): {readable}")

    if problems:
        pytest.fail(f"Table '{table_name}': " + "; ".join(problems))


# ============================================================================
# EXERCISES -- one CREATE TABLE per table, in dependency order
# ============================================================================

def test_01_create_person(cursor):
    """
    Exercise 1: Person

    Create the Person table, based on the ER model.
    """
    sql = """
CREATE TABLE Person (
    PersonID        CHAR(6) PRIMARY KEY,
    FullName        VARCHAR(120) NOT NULL,
    InstitutionalEmail VARCHAR(120) NOT NULL UNIQUE,
    PhoneNumber     VARCHAR(25),
    Affiliation     VARCHAR(120)
)
    """
    assert_table_matches_expected(cursor, sql, "Person")


def test_02_create_serviceprovider(cursor):
    """
    Exercise 2: ServiceProvider

    Create the ServiceProvider table, based on the ER model.
    """
    sql = """
CREATE TABLE ServiceProvider (
    ProviderID        CHAR(6) PRIMARY KEY,
    CompanyName       VARCHAR(120) NOT NULL,
    ContactPerson     VARCHAR(100),
    Phone             VARCHAR(25),
    ContractReference VARCHAR(60)
)
    """
    assert_table_matches_expected(cursor, sql, "ServiceProvider")


def test_03_create_researchproject(cursor):
    """
    Exercise 3: ResearchProject

    Create the ResearchProject table, based on the ER model.
    """
    sql = """
CREATE TABLE ResearchProject (
    ProjectCode   CHAR(6) PRIMARY KEY,
    Title         VARCHAR(150) NOT NULL,
    StartDate     DATE,
    EndDate       DATE,
    FundingSource VARCHAR(100),
    Status        VARCHAR(30)
)
    """
    assert_table_matches_expected(cursor, sql, "ResearchProject")


def test_04_create_equipmentmodel(cursor):
    """
    Exercise 4: EquipmentModel

    Create the EquipmentModel table, based on the ER model.
    """
    sql = """
CREATE TABLE EquipmentModel (
    ModelID                  CHAR(6) PRIMARY KEY,
    CommercialName           VARCHAR(100) NOT NULL,
    Manufacturer             VARCHAR(100),
    Category                 VARCHAR(60),
    RequiredEnvironment      VARCHAR(100),
    SpecialTrainingMandatory BOOLEAN
)
    """
    assert_table_matches_expected(cursor, sql, "EquipmentModel")


def test_05_create_certification(cursor):
    """
    Exercise 5: Certification

    Create the Certification table, based on the ER model.
    """
    sql = """
CREATE TABLE Certification (
    CertificationCode CHAR(6) PRIMARY KEY,
    Title             VARCHAR(120) NOT NULL,
    IssuingAuthority  VARCHAR(100),
    ValidityPeriod    INT,
    SafetyLevel       VARCHAR(30)
)
    """
    assert_table_matches_expected(cursor, sql, "Certification")


def test_06_create_consumable(cursor):
    """
    Exercise 6: Consumable

    Create the Consumable table, based on the ER model.
    """
    sql = """
CREATE TABLE Consumable (
    ConsumableID     CHAR(6) PRIMARY KEY,
    Name             VARCHAR(100) NOT NULL,
    UnitOfMeasure    VARCHAR(30),
    HazardLevel      VARCHAR(30),
    ReorderThreshold INT,
    Supplier         VARCHAR(100)
)
    """
    assert_table_matches_expected(cursor, sql, "Consumable")


def test_07_create_researchuser(cursor):
    """
    Exercise 7: ResearchUser

    Create the ResearchUser table, based on the ER model.
    """
    sql = """
CREATE TABLE ResearchUser (
    PersonID            CHAR(6) PRIMARY KEY,
    AcademicCategory    VARCHAR(60),
    InstitutionalStatus VARCHAR(60),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "ResearchUser")


def test_08_create_technicalstaff(cursor):
    """
    Exercise 8: TechnicalStaff

    Create the TechnicalStaff table, based on the ER model.
    """
    sql = """
CREATE TABLE TechnicalStaff (
    PersonID      CHAR(6) PRIMARY KEY,
    Role          VARCHAR(60),
    ExpertiseArea VARCHAR(100),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "TechnicalStaff")


def test_09_create_laboratory(cursor):
    """
    Exercise 9: Laboratory

    Create the Laboratory table, based on the ER model.
    """
    sql = """
CREATE TABLE Laboratory (
    LabID        CHAR(6) PRIMARY KEY,
    Name         VARCHAR(100) NOT NULL,
    Building     VARCHAR(50),
    RoomNumber   VARCHAR(20),
    ResearchArea VARCHAR(100),
    SupervisorID CHAR(6),
    FOREIGN KEY (SupervisorID) REFERENCES ResearchUser(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "Laboratory")


def test_10_create_internaltechnician(cursor):
    """
    Exercise 10: InternalTechnician

    Create the InternalTechnician table, based on the ER model.
    """
    sql = """
CREATE TABLE InternalTechnician (
    PersonID CHAR(6) PRIMARY KEY,
    HireDate DATE,
    FOREIGN KEY (PersonID) REFERENCES TechnicalStaff(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "InternalTechnician")


def test_11_create_externaltechnician(cursor):
    """
    Exercise 11: ExternalTechnician

    Create the ExternalTechnician table, based on the ER model.
    """
    sql = """
CREATE TABLE ExternalTechnician (
    PersonID          CHAR(6) PRIMARY KEY,
    CompanyName       VARCHAR(120),
    ContractReference VARCHAR(60),
    ProviderID        CHAR(6),
    FOREIGN KEY (PersonID) REFERENCES TechnicalStaff(PersonID),
    FOREIGN KEY (ProviderID) REFERENCES ServiceProvider(ProviderID)
)
    """
    assert_table_matches_expected(cursor, sql, "ExternalTechnician")


def test_12_create_attachedto(cursor):
    """
    Exercise 12: AttachedTo

    Create the AttachedTo table, based on the ER model.
    """
    sql = """
CREATE TABLE AttachedTo (
    PersonID CHAR(6),
    LabID    CHAR(6),
    PRIMARY KEY (PersonID, LabID),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID)
)
    """
    assert_table_matches_expected(cursor, sql, "AttachedTo")


def test_13_create_projectparticipation(cursor):
    """
    Exercise 13: ProjectParticipation

    Create the ProjectParticipation table, based on the ER model.
    """
    sql = """
CREATE TABLE ProjectParticipation (
    PersonID    CHAR(6),
    ProjectCode CHAR(6),
    ProjectRole VARCHAR(50),
    PRIMARY KEY (PersonID, ProjectCode),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode)
)
    """
    assert_table_matches_expected(cursor, sql, "ProjectParticipation")


def test_14_create_equipmentunit(cursor):
    """
    Exercise 14: EquipmentUnit

    Create the EquipmentUnit table, based on the ER model.
    """
    sql = """
CREATE TABLE EquipmentUnit (
    SerialNumber    CHAR(10) PRIMARY KEY,
    AcquisitionDate DATE,
    PurchaseCost    DECIMAL(10,2),
    CurrentStatus   VARCHAR(30),
    IsPortable      BOOLEAN,
    LabID           CHAR(6),
    ModelID         CHAR(6),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID),
    FOREIGN KEY (ModelID) REFERENCES EquipmentModel(ModelID)
)
    """
    assert_table_matches_expected(cursor, sql, "EquipmentUnit")


def test_15_create_holdscertification(cursor):
    """
    Exercise 15: HoldsCertification

    Create the HoldsCertification table, based on the ER model.
    """
    sql = """
CREATE TABLE HoldsCertification (
    PersonID          CHAR(6),
    CertificationCode CHAR(6),
    IssueDate         DATE,
    ExpirationDate    DATE,
    ResultOrGrade     VARCHAR(30),
    PRIMARY KEY (PersonID, CertificationCode),
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (CertificationCode) REFERENCES Certification(CertificationCode)
)
    """
    assert_table_matches_expected(cursor, sql, "HoldsCertification")


def test_16_create_requirescertification(cursor):
    """
    Exercise 16: RequiresCertification

    Create the RequiresCertification table, based on the ER model.
    """
    sql = """
CREATE TABLE RequiresCertification (
    ModelID           CHAR(6),
    CertificationCode CHAR(6),
    PRIMARY KEY (ModelID, CertificationCode),
    FOREIGN KEY (ModelID) REFERENCES EquipmentModel(ModelID),
    FOREIGN KEY (CertificationCode) REFERENCES Certification(CertificationCode)
)
    """
    assert_table_matches_expected(cursor, sql, "RequiresCertification")


def test_17_create_stores(cursor):
    """
    Exercise 17: Stores

    Create the Stores table, based on the ER model.
    """
    sql = """
CREATE TABLE Stores (
    LabID             CHAR(6),
    ConsumableID      CHAR(6),
    QuantityAvailable INT,
    StorageCondition  VARCHAR(60),
    LastRestockDate   DATE,
    PRIMARY KEY (LabID, ConsumableID),
    FOREIGN KEY (LabID) REFERENCES Laboratory(LabID),
    FOREIGN KEY (ConsumableID) REFERENCES Consumable(ConsumableID)
)
    """
    assert_table_matches_expected(cursor, sql, "Stores")


def test_18_create_reservation(cursor):
    """
    Exercise 18: Reservation

    Create the Reservation table, based on the ER model.
    """
    sql = """
CREATE TABLE Reservation (
    ReservationID       CHAR(6) PRIMARY KEY,
    SubmissionTimestamp DATETIME,
    PlannedStartTime    DATETIME,
    PlannedEndTime       DATETIME,
    Purpose             VARCHAR(150),
    Status              VARCHAR(20),
    PersonID            CHAR(6) NOT NULL,
    SerialNumber        CHAR(10) NOT NULL,
    ProjectCode         CHAR(6),
    ApprovedBy          CHAR(6),
    FOREIGN KEY (PersonID) REFERENCES ResearchUser(PersonID),
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode),
    FOREIGN KEY (ApprovedBy) REFERENCES Person(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "Reservation")


def test_19_create_maintenance(cursor):
    """
    Exercise 19: Maintenance

    Create the Maintenance table, based on the ER model.
    """
    sql = """
CREATE TABLE Maintenance (
    MaintenanceID    CHAR(6) PRIMARY KEY,
    MaintenanceDate  DATE,
    MaintenanceType  VARCHAR(30),
    Description      VARCHAR(255),
    Cost             DECIMAL(10,2),
    DowntimeDuration INT,
    Outcome          VARCHAR(100),
    SerialNumber     CHAR(10) NOT NULL,
    TechnicianID     CHAR(6) NOT NULL,
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (TechnicianID) REFERENCES TechnicalStaff(PersonID)
)
    """
    assert_table_matches_expected(cursor, sql, "Maintenance")


def test_20_create_calibrationrecord(cursor):
    """
    Exercise 20: CalibrationRecord

    Create the CalibrationRecord table, based on the ER model.
    """
    sql = """
CREATE TABLE CalibrationRecord (
    SerialNumber    CHAR(10),
    CalibrationNumber INT,
    CalibrationDate DATE,
    CalibrationType VARCHAR(30),
    Result          VARCHAR(30),
    NextDueDate     DATE,
    Remarks         VARCHAR(255),
    PRIMARY KEY (SerialNumber, CalibrationNumber),
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber)
)
    """
    assert_table_matches_expected(cursor, sql, "CalibrationRecord")


def test_21_create_usagesession(cursor):
    """
    Exercise 21: UsageSession

    Create the UsageSession table, based on the ER model.
    """
    sql = """
CREATE TABLE UsageSession (
    SessionID       CHAR(6) PRIMARY KEY,
    ActualStartTime DATETIME,
    ActualEndTime   DATETIME,
    Purpose         VARCHAR(150),
    Outcome         VARCHAR(100),
    SerialNumber    CHAR(10) NOT NULL,
    ResearchUserID  CHAR(6) NOT NULL,
    ReservationID   CHAR(6),
    ProjectCode     CHAR(6),
    FOREIGN KEY (SerialNumber) REFERENCES EquipmentUnit(SerialNumber),
    FOREIGN KEY (ResearchUserID) REFERENCES ResearchUser(PersonID),
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
    FOREIGN KEY (ProjectCode) REFERENCES ResearchProject(ProjectCode)
)
    """
    assert_table_matches_expected(cursor, sql, "UsageSession")


def test_22_create_consumes(cursor):
    """
    Exercise 22: Consumes

    Create the Consumes table, based on the ER model.
    """
    sql = """
CREATE TABLE Consumes (
    SessionID    CHAR(6),
    ConsumableID CHAR(6),
    QuantityUsed INT,
    PRIMARY KEY (SessionID, ConsumableID),
    FOREIGN KEY (SessionID) REFERENCES UsageSession(SessionID),
    FOREIGN KEY (ConsumableID) REFERENCES Consumable(ConsumableID)
)
    """
    assert_table_matches_expected(cursor, sql, "Consumes")