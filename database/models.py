from sqlalchemy import Column, Integer, String, Date, Float, Time, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Patient(Base):
    __tablename__ = "Patient"

    PatientID = Column(Integer, primary_key=True, index=True)
    Patient_FIO = Column(String, nullable=False)
    Patient_BirthDate = Column(Date, nullable=False)
    Patient_Address = Column(String)
    Patient_Phone = Column(String)
    PolyclinicID = Column(Integer, ForeignKey("Polyclinic.PolyclinicID"), nullable=False)


class Doctor(Base):
    __tablename__ = "Doctor"

    DoctorID = Column(Integer, primary_key=True, index=True)
    Doctor_FIO = Column(String, nullable=False)
    Doctor_BirthDate = Column(Date, nullable=False)
    Doctor_Specialization = Column(String, nullable=False)
    Doctor_Phone = Column(String)
    PolyclinicID = Column(Integer, ForeignKey("Polyclinic.PolyclinicID"), nullable=False)


class Session(Base):
    __tablename__ = "Session"

    SessionID = Column(Integer, primary_key=True, index=True)
    Session_Date = Column(Date, nullable=False)
    Session_StartTime = Column(String, nullable=False)  # Время можно хранить как строку или Time
    Session_EndTime = Column(String, nullable=False)
    PatientID = Column(Integer, ForeignKey("Patient.PatientID"), nullable=False)
    DoctorID = Column(Integer, ForeignKey("Doctor.DoctorID"), nullable=False)
    LabID = Column(Integer, ForeignKey("Laboratory.LabID"), nullable=False)


class ECS_Data(Base):
    __tablename__ = "ECS_Data"

    ECSDataID = Column(Integer, primary_key=True, index=True)
    SessionID = Column(Integer, ForeignKey("Session.SessionID"), nullable=False)
    RR_Length = Column(Integer, nullable=False)
    RR_Time = Column(Float, nullable=False)


class PG_Data(Base):
    __tablename__ = "PG_Data"

    PGDataID = Column(Integer, primary_key=True, index=True)
    SessionID = Column(Integer, ForeignKey("Session.SessionID"), nullable=False)
    D1 = Column(Integer, nullable=False)
    D2 = Column(Integer, nullable=False)
    Amplitude = Column(Float)


# Таблица "Поликлиника"
class Polyclinic(Base):
    __tablename__ = "Polyclinic"

    PolyclinicID = Column(Integer, primary_key=True, index=True)
    Polyclinic_Name = Column(String(255), nullable=False)
    Polyclinic_Address = Column(String(255), nullable=False)
    Polyclinic_Phone = Column(String(20))


# Таблица "Регистратура"
class Registration(Base):
    __tablename__ = "Registration"

    RegistrationID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("Patient.PatientID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    PolyclinicID = Column(Integer, ForeignKey("Polyclinic.PolyclinicID", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    Registration_Date = Column(Date, nullable=False)
    Registration_Time = Column(Time, nullable=False)


# Таблица "Лаборатория"
class Laboratory(Base):
    __tablename__ = "Laboratory"

    LabID = Column(Integer, primary_key=True, index=True)
    Lab_Name = Column(String(255), nullable=False)
    Lab_Address = Column(String(255), nullable=False)
    PolyclinicID = Column(Integer, ForeignKey("Polyclinic.PolyclinicID", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)


# Таблица "Оборудование"
class Equipment(Base):
    __tablename__ = "Equipment"

    EquipmentID = Column(Integer, primary_key=True, index=True)
    Equipment_Name = Column(String(255), nullable=False)
    Equipment_Serial = Column(String(50), nullable=False)  # Custom domain EquipmentSerial
    LabID = Column(Integer, ForeignKey("Laboratory.LabID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


# Таблица "Результаты анализа"
class Analysis_Result(Base):
    __tablename__ = "Analysis_Result"

    AnalysisResultID = Column(Integer, primary_key=True, index=True)
    SessionID = Column(Integer, ForeignKey("Session.SessionID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    RR_Analysis = Column(Text, nullable=False)
    DU_Analysis = Column(Text, nullable=False)


# Таблица "График работы врачей"
class Doctor_Schedule(Base):
    __tablename__ = "Doctor_Schedule"

    ScheduleID = Column(Integer, primary_key=True, index=True)
    DoctorID = Column(Integer, ForeignKey("Doctor.DoctorID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    WorkDate = Column(Date, nullable=False)
    StartTime = Column(Time, nullable=False)
    EndTime = Column(Time, nullable=False)


# Таблица "Диагноз"
class Diagnosis(Base):
    __tablename__ = "Diagnosis"

    DiagnosisID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("Patient.PatientID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    DiagnosisName = Column(String(255))
    Description = Column(Text, nullable=False)
    DateOfDiagnosis = Column(Date, nullable=False)
    DoctorID = Column(Integer, ForeignKey("Doctor.DoctorID", ondelete="CASCADE", onupdate="CASCADE"))


# Таблица "Хронические заболевания"
class Chronic_Condition(Base):
    __tablename__ = "Chronic_Condition"

    ChronicID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("Patient.PatientID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ConditionName = Column(String(255), nullable=False)
    DiagnosisDate = Column(Date)
    Remarks = Column(Text)


# Таблица "Рекомендации по лечению"
class Treatment_Recommendation(Base):
    __tablename__ = "Treatment_Recommendation"

    RecommendationID = Column(Integer, primary_key=True, index=True)
    DiagnosisID = Column(Integer, ForeignKey("Diagnosis.DiagnosisID", ondelete="CASCADE", onupdate="CASCADE"),
                         nullable=False)
    TreatmentPlan = Column(Text, nullable=False)
    AdditionalRemarks = Column(Text)


# Таблица "Вид деятельности"
class Activity_Type(Base):
    __tablename__ = "Activity_Type"

    ActivityTypeID = Column(Integer, primary_key=True, index=True)
    ActivityName = Column(String(255), nullable=False)
    Description = Column(Text)


# Таблица "Вид деятельности пациента"
class Patient_Activity(Base):
    __tablename__ = "Patient_Activity"

    PatientActivityID = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey("Patient.PatientID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ActivityTypeID = Column(Integer, ForeignKey("Activity_Type.ActivityTypeID", ondelete="CASCADE", onupdate="CASCADE"),
                            nullable=False)
