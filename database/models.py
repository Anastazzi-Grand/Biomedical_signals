from sqlalchemy import Column, Integer, String, Date, Float, Time, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patient"
    patientid = Column(Integer, primary_key=True, index=True)
    patient_fio = Column(String, nullable=False)
    patient_birthdate = Column(Date, nullable=False)
    patient_address = Column(String)
    patient_phone = Column(String)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid"), nullable=False)

    # Связи
    registrations = relationship("Registration", back_populates="patient")
    sessions = relationship("Sessions", back_populates="patient")
    diagnoses = relationship("Diagnosis", back_populates="patient")
    chronic_conditions = relationship("Chronic_condition", back_populates="patient")
    activities = relationship("Patient_activity", back_populates="patient")
    polyclinic = relationship("Polyclinic", back_populates="patients")


class Doctor(Base):
    __tablename__ = "doctor"
    doctorid = Column(Integer, primary_key=True, index=True)
    doctor_fio = Column(String, nullable=False)
    doctor_birthdate = Column(Date, nullable=False)
    doctor_specialization = Column(String, nullable=False)
    doctor_phone = Column(String)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid"), nullable=False)

    # Связи
    sessions = relationship("Sessions", back_populates="doctor")
    schedules = relationship("Doctor_schedule", back_populates="doctor")
    diagnoses = relationship("Diagnosis", back_populates="doctor")
    polyclinic = relationship("Polyclinic", back_populates="doctors")


class Sessions(Base):
    __tablename__ = "session"
    sessionid = Column(Integer, primary_key=True, index=True)
    session_date = Column(Date, nullable=False)
    session_starttime = Column(Time, nullable=False)
    session_endtime = Column(Time, nullable=False)
    patientid = Column(Integer, ForeignKey("patient.patientid"), nullable=False)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid"), nullable=False)
    labid = Column(Integer, ForeignKey("laboratory.labid"), nullable=False)

    # Связи
    patient = relationship("Patient", back_populates="sessions")
    doctor = relationship("Doctor", back_populates="sessions")
    laboratory = relationship("Laboratory", back_populates="sessions")
    ecs_data = relationship("ECS_data", back_populates="session")
    pg_data = relationship("PG_data", back_populates="session")
    analysis_results = relationship("Analysis_result", back_populates="session")


class ECS_data(Base):
    __tablename__ = "ecs_data"
    ecsdataid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid"), nullable=False)
    rr_length = Column(Integer, nullable=False)
    rr_time = Column(Float, nullable=False)

    # Связи
    session = relationship("Sessions", back_populates="ecs_data")


class PG_data(Base):
    __tablename__ = "pg_data"
    pgdataid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid"), nullable=False)
    d1 = Column(Integer, nullable=False)
    d2 = Column(Integer, nullable=False)
    amplitude = Column(Float)

    # Связи
    session = relationship("Sessions", back_populates="pg_data")


class Polyclinic(Base):
    __tablename__ = "polyclinic"
    polyclinicid = Column(Integer, primary_key=True, index=True)
    polyclinic_name = Column(String(255), nullable=False)
    polyclinic_address = Column(String(255), nullable=False)
    polyclinic_phone = Column(String(20))

    # Связи
    patients = relationship("Patient", back_populates="polyclinic")
    doctors = relationship("Doctor", back_populates="polyclinic")
    laboratories = relationship("Laboratory", back_populates="polyclinic")
    registrations = relationship("Registration", back_populates="polyclinic")


class Registration(Base):
    __tablename__ = "registration"
    registrationid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    registration_date = Column(Date, nullable=False)
    registration_time = Column(Time, nullable=False)

    # Связи
    patient = relationship("Patient", back_populates="registrations")
    polyclinic = relationship("Polyclinic", back_populates="registrations")


class Laboratory(Base):
    __tablename__ = "laboratory"
    labid = Column(Integer, primary_key=True, index=True)
    lab_name = Column(String(255), nullable=False)
    lab_address = Column(String(255), nullable=False)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Связи
    polyclinic = relationship("Polyclinic", back_populates="laboratories")
    sessions = relationship("Sessions", back_populates="laboratory")
    equipment = relationship("Equipment", back_populates="laboratory")


class Equipment(Base):
    __tablename__ = "equipment"
    equipmentid = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String(255), nullable=False)
    equipment_serial = Column(String(50), nullable=False)  # Custom domain EquipmentSerial
    labid = Column(Integer, ForeignKey("laboratory.labid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Связи
    laboratory = relationship("Laboratory", back_populates="equipment")


class Analysis_result(Base):
    __tablename__ = "analysis_result"
    analysisresultid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    rr_analysis = Column(Text, nullable=False)
    du_analysis = Column(Text, nullable=False)

    # Связи
    session = relationship("Sessions", back_populates="analysis_results")


class Doctor_schedule(Base):
    __tablename__ = "doctor_schedule"
    scheduleid = Column(Integer, primary_key=True, index=True)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    workdate = Column(Date, nullable=False)
    starttime = Column(Time, nullable=False)
    endtime = Column(Time, nullable=False)

    # Связи
    doctor = relationship("Doctor", back_populates="schedules")


class Diagnosis(Base):
    __tablename__ = "diagnosis"
    diagnosisid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    diagnosisname = Column(String(255))
    description = Column(Text, nullable=False)
    dateofdiagnosis = Column(Date, nullable=False)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid", ondelete="CASCADE", onupdate="CASCADE"))

    # Связи
    patient = relationship("Patient", back_populates="diagnoses")
    doctor = relationship("Doctor", back_populates="diagnoses")
    recommendations = relationship("Treatment_recommendation", back_populates="diagnosis")


class Chronic_condition(Base):
    __tablename__ = "chronic_condition"
    chronicid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    conditionname = Column(String(255), nullable=False)
    diagnosisdate = Column(Date)
    remarks = Column(Text)

    # Связи
    patient = relationship("Patient", back_populates="chronic_conditions")


class Treatment_recommendation(Base):
    __tablename__ = "treatment_recommendation"
    recommendationid = Column(Integer, primary_key=True, index=True)
    diagnosisid = Column(Integer, ForeignKey("diagnosis.diagnosisid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    treatmentplan = Column(Text, nullable=False)
    additionalremarks = Column(Text)

    # Связи
    diagnosis = relationship("Diagnosis", back_populates="recommendations")


class Activity_type(Base):
    __tablename__ = "activity_type"
    activitytypeid = Column(Integer, primary_key=True, index=True)
    activityname = Column(String(255), nullable=False)
    description = Column(Text)

    # Связи
    patient_activities = relationship("Patient_activity", back_populates="activity_type")


class Patient_activity(Base):
    __tablename__ = "patient_activity"
    patientactivityid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    activitytypeid = Column(Integer, ForeignKey("activity_type.activitytypeid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Связи
    patient = relationship("Patient", back_populates="activities")
    activity_type = relationship("Activity_type", back_populates="patient_activities")
