from sqlalchemy import Column, Integer, String, Date, Float, Time, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patient"

    patientid = Column(Integer, primary_key=True, index=True)
    patient_fio = Column(String, nullable=False)
    patient_birthdate = Column(Date, nullable=False)
    patient_address = Column(String)
    patient_phone = Column(String)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid"), nullable=False)


class Doctor(Base):
    __tablename__ = "doctor"

    doctorid = Column(Integer, primary_key=True, index=True)
    doctor_fio = Column(String, nullable=False)
    doctor_birthdate = Column(Date, nullable=False)
    doctor_specialization = Column(String, nullable=False)
    doctor_phone = Column(String)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid"), nullable=False)


class Sessions(Base):
    __tablename__ = "session"

    sessionid = Column(Integer, primary_key=True, index=True)
    session_date = Column(Date, nullable=False)
    session_starttime = Column(Time, nullable=False)
    session_endtime = Column(Time, nullable=False)
    patientid = Column(Integer, ForeignKey("patient.patientid"), nullable=False)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid"), nullable=False)
    labid = Column(Integer, ForeignKey("laboratory.labid"), nullable=False)


class ECS_data(Base):
    __tablename__ = "ecs_data"

    ecsdataid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid"), nullable=False)
    rr_length = Column(Integer, nullable=False)
    rr_time = Column(Float, nullable=False)


class PG_data(Base):
    __tablename__ = "pg_data"

    pgdataid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid"), nullable=False)
    d1 = Column(Integer, nullable=False)
    d2 = Column(Integer, nullable=False)
    amplitude = Column(Float)


class Polyclinic(Base):
    __tablename__ = "polyclinic"

    polyclinicid = Column(Integer, primary_key=True, index=True)
    polyclinic_name = Column(String(255), nullable=False)
    polyclinic_address = Column(String(255), nullable=False)
    polyclinic_phone = Column(String(20))


class Registration(Base):
    __tablename__ = "registration"

    registrationid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    registration_date = Column(Date, nullable=False)
    registration_time = Column(Time, nullable=False)


class Laboratory(Base):
    __tablename__ = "laboratory"

    labid = Column(Integer, primary_key=True, index=True)
    lab_name = Column(String(255), nullable=False)
    lab_address = Column(String(255), nullable=False)
    polyclinicid = Column(Integer, ForeignKey("polyclinic.polyclinicid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class Equipment(Base):
    __tablename__ = "equipment"

    equipmentid = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String(255), nullable=False)
    equipment_serial = Column(String(50), nullable=False)  # Custom domain EquipmentSerial
    labid = Column(Integer, ForeignKey("laboratory.labid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class Analysis_result(Base):
    __tablename__ = "analysis_result"

    analysisresultid = Column(Integer, primary_key=True, index=True)
    sessionid = Column(Integer, ForeignKey("session.sessionid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    rr_analysis = Column(Text, nullable=False)
    du_analysis = Column(Text, nullable=False)


class Doctor_schedule(Base):
    __tablename__ = "doctor_schedule"

    scheduleid = Column(Integer, primary_key=True, index=True)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    workdate = Column(Date, nullable=False)
    starttime = Column(Time, nullable=False)
    endtime = Column(Time, nullable=False)


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    diagnosisid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    diagnosis_name = Column(String(255))
    description = Column(Text, nullable=False)
    date_of_diagnosis = Column(Date, nullable=False)
    doctorid = Column(Integer, ForeignKey("doctor.doctorid", ondelete="CASCADE", onupdate="CASCADE"))


class Chronic_condition(Base):
    __tablename__ = "chronic_condition"

    chronicid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    condition_name = Column(String(255), nullable=False)
    diagnosis_date = Column(Date)
    remarks = Column(Text)


class Treatment_recommendation(Base):
    __tablename__ = "treatment_recommendation"

    recommendationid = Column(Integer, primary_key=True, index=True)
    diagnosisid = Column(Integer, ForeignKey("diagnosis.diagnosisid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    treatment_plan = Column(Text, nullable=False)
    additional_remarks = Column(Text)


class Activity_type(Base):
    __tablename__ = "activity_type"

    activitytypeid = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String(255), nullable=False)
    description = Column(Text)


class Patient_activity(Base):
    __tablename__ = "patient_activity"

    patientactivityid = Column(Integer, primary_key=True, index=True)
    patientid = Column(Integer, ForeignKey("patient.patientid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    activitytypeid = Column(Integer, ForeignKey("activity_type.activitytypeid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)