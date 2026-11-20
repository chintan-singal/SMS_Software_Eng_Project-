-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: student_management
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `AdminID` int NOT NULL,
  `RoleType` enum('SuperAdmin','DeptAdmin','FinanceAdmin') NOT NULL,
  PRIMARY KEY (`AdminID`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`AdminID`) REFERENCES `person` (`PersonID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `announcement`
--

DROP TABLE IF EXISTS `announcement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcement` (
  `AnnouncementID` int NOT NULL AUTO_INCREMENT,
  `PostedBy` int NOT NULL,
  `Message` text NOT NULL,
  `DatePosted` datetime NOT NULL,
  PRIMARY KEY (`AnnouncementID`),
  KEY `PostedBy` (`PostedBy`),
  CONSTRAINT `announcement_ibfk_1` FOREIGN KEY (`PostedBy`) REFERENCES `person` (`PersonID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `announcementcourse`
--

DROP TABLE IF EXISTS `announcementcourse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcementcourse` (
  `AnnouncementID` int NOT NULL,
  `CourseID` int NOT NULL,
  PRIMARY KEY (`AnnouncementID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `announcementcourse_ibfk_1` FOREIGN KEY (`AnnouncementID`) REFERENCES `announcement` (`AnnouncementID`) ON DELETE CASCADE,
  CONSTRAINT `announcementcourse_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `announcementdepartment`
--

DROP TABLE IF EXISTS `announcementdepartment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcementdepartment` (
  `AnnouncementID` int NOT NULL,
  `DepartmentID` int NOT NULL,
  PRIMARY KEY (`AnnouncementID`,`DepartmentID`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `announcementdepartment_ibfk_1` FOREIGN KEY (`AnnouncementID`) REFERENCES `announcement` (`AnnouncementID`) ON DELETE CASCADE,
  CONSTRAINT `announcementdepartment_ibfk_2` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment`
--

DROP TABLE IF EXISTS `assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment` (
  `AssignmentID` int NOT NULL AUTO_INCREMENT,
  `CourseID` int NOT NULL,
  `CreatedBy` int NOT NULL,
  `Title` varchar(120) NOT NULL,
  `Description` text,
  `Deadline` datetime NOT NULL,
  `MaxMarks` int NOT NULL,
  PRIMARY KEY (`AssignmentID`),
  KEY `CourseID` (`CourseID`),
  KEY `CreatedBy` (`CreatedBy`),
  CONSTRAINT `assignment_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`),
  CONSTRAINT `assignment_ibfk_2` FOREIGN KEY (`CreatedBy`) REFERENCES `faculty` (`FacultyID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignmentdocument`
--

DROP TABLE IF EXISTS `assignmentdocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignmentdocument` (
  `AssignmentID` int NOT NULL,
  `DocumentID` int NOT NULL,
  PRIMARY KEY (`AssignmentID`,`DocumentID`),
  KEY `DocumentID` (`DocumentID`),
  CONSTRAINT `assignmentdocument_ibfk_1` FOREIGN KEY (`AssignmentID`) REFERENCES `assignment` (`AssignmentID`) ON DELETE CASCADE,
  CONSTRAINT `assignmentdocument_ibfk_2` FOREIGN KEY (`DocumentID`) REFERENCES `document` (`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `AttendanceID` int NOT NULL AUTO_INCREMENT,
  `CourseID` int NOT NULL,
  `StudentID` int NOT NULL,
  `RecordedBy` int NOT NULL,
  `ClassDate` date NOT NULL,
  `Status` enum('Present','Absent') NOT NULL,
  `VerifiedBy` int DEFAULT NULL,
  `VerifiedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`AttendanceID`),
  UNIQUE KEY `CourseID` (`CourseID`,`StudentID`,`ClassDate`),
  KEY `StudentID` (`StudentID`),
  KEY `RecordedBy` (`RecordedBy`),
  KEY `VerifiedBy` (`VerifiedBy`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`),
  CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`RecordedBy`) REFERENCES `faculty` (`FacultyID`),
  CONSTRAINT `attendance_ibfk_4` FOREIGN KEY (`VerifiedBy`) REFERENCES `admin` (`AdminID`)
) ENGINE=InnoDB AUTO_INCREMENT=5306 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `CourseID` int NOT NULL AUTO_INCREMENT,
  `CourseName` varchar(120) NOT NULL,
  `Credits` int NOT NULL,
  `DepartmentID` int NOT NULL,
  `Semester` int NOT NULL,
  PRIMARY KEY (`CourseID`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB AUTO_INCREMENT=3006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coursedocument`
--

DROP TABLE IF EXISTS `coursedocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coursedocument` (
  `CourseID` int NOT NULL,
  `DocumentID` int NOT NULL,
  PRIMARY KEY (`CourseID`,`DocumentID`),
  KEY `DocumentID` (`DocumentID`),
  CONSTRAINT `coursedocument_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`) ON DELETE CASCADE,
  CONSTRAINT `coursedocument_ibfk_2` FOREIGN KEY (`DocumentID`) REFERENCES `document` (`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `DepartmentID` int NOT NULL AUTO_INCREMENT,
  `DeptCode` varchar(20) NOT NULL,
  `DeptName` varchar(100) NOT NULL,
  PRIMARY KEY (`DepartmentID`),
  UNIQUE KEY `DeptCode` (`DeptCode`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document`
--

DROP TABLE IF EXISTS `document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document` (
  `DocumentID` int NOT NULL AUTO_INCREMENT,
  `UploadedBy` int NOT NULL,
  `Title` varchar(150) NOT NULL,
  `FileType` varchar(16) NOT NULL,
  `FilePath` varchar(255) NOT NULL,
  `UploadedOn` datetime NOT NULL,
  `AccessLevel` enum('Public','CourseOnly','Private') NOT NULL,
  PRIMARY KEY (`DocumentID`),
  KEY `UploadedBy` (`UploadedBy`),
  CONSTRAINT `document_ibfk_1` FOREIGN KEY (`UploadedBy`) REFERENCES `person` (`PersonID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `enrollment`
--

DROP TABLE IF EXISTS `enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollment` (
  `EnrollmentID` int NOT NULL AUTO_INCREMENT,
  `StudentID` int NOT NULL,
  `CourseID` int NOT NULL,
  `EnrollmentDate` date NOT NULL,
  `Status` enum('Active','Dropped','Completed') NOT NULL,
  PRIMARY KEY (`EnrollmentID`),
  UNIQUE KEY `StudentID` (`StudentID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`),
  CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`)
) ENGINE=InnoDB AUTO_INCREMENT=421 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam`
--

DROP TABLE IF EXISTS `exam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam` (
  `ExamID` int NOT NULL AUTO_INCREMENT,
  `CourseID` int NOT NULL,
  `ConductedBy` int NOT NULL,
  `ExamType` enum('Midterm','Final','Quiz') NOT NULL,
  `ExamDate` datetime NOT NULL,
  `MaxMarks` int NOT NULL,
  PRIMARY KEY (`ExamID`),
  KEY `CourseID` (`CourseID`),
  KEY `ConductedBy` (`ConductedBy`),
  CONSTRAINT `exam_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`),
  CONSTRAINT `exam_ibfk_2` FOREIGN KEY (`ConductedBy`) REFERENCES `faculty` (`FacultyID`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examevaluation`
--

DROP TABLE IF EXISTS `examevaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examevaluation` (
  `EvaluationID` int NOT NULL AUTO_INCREMENT,
  `ExamResultID` int NOT NULL,
  `FacultyID` int NOT NULL,
  `MarksGiven` int NOT NULL,
  `Comments` text,
  `EvaluatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`EvaluationID`),
  KEY `ExamResultID` (`ExamResultID`),
  KEY `FacultyID` (`FacultyID`),
  CONSTRAINT `examevaluation_ibfk_1` FOREIGN KEY (`ExamResultID`) REFERENCES `examresult` (`ExamResultID`) ON DELETE CASCADE,
  CONSTRAINT `examevaluation_ibfk_2` FOREIGN KEY (`FacultyID`) REFERENCES `faculty` (`FacultyID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `examresult`
--

DROP TABLE IF EXISTS `examresult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examresult` (
  `ExamResultID` int NOT NULL AUTO_INCREMENT,
  `ExamID` int NOT NULL,
  `StudentID` int NOT NULL,
  `MarksObtained` int NOT NULL,
  `Grade` char(2) DEFAULT NULL,
  PRIMARY KEY (`ExamResultID`),
  UNIQUE KEY `ExamID` (`ExamID`,`StudentID`),
  KEY `StudentID` (`StudentID`),
  CONSTRAINT `examresult_ibfk_1` FOREIGN KEY (`ExamID`) REFERENCES `exam` (`ExamID`) ON DELETE CASCADE,
  CONSTRAINT `examresult_ibfk_2` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`)
) ENGINE=InnoDB AUTO_INCREMENT=5208 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `FacultyID` int NOT NULL,
  `Designation` varchar(60) DEFAULT NULL,
  `DepartmentID` int NOT NULL,
  `Qualification` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`FacultyID`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`FacultyID`) REFERENCES `person` (`PersonID`),
  CONSTRAINT `faculty_ibfk_2` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `FeedbackID` int NOT NULL AUTO_INCREMENT,
  `StudentID` int NOT NULL,
  `FacultyID` int NOT NULL,
  `CourseID` int NOT NULL,
  `Rating` int NOT NULL,
  `Comments` text,
  `CreatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`FeedbackID`),
  KEY `CourseID` (`CourseID`),
  KEY `idx_feedback_faculty` (`FacultyID`,`CourseID`,`CreatedAt`),
  KEY `idx_feedback_student` (`StudentID`,`CreatedAt`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`),
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`FacultyID`) REFERENCES `faculty` (`FacultyID`),
  CONSTRAINT `feedback_ibfk_3` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`),
  CONSTRAINT `feedback_chk_1` CHECK ((`Rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `StudentID` int NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentDate` datetime NOT NULL,
  `PaymentType` enum('Tuition','Fine','Hostel','Other') NOT NULL,
  `Status` enum('Paid','Pending') NOT NULL,
  PRIMARY KEY (`PaymentID`),
  KEY `StudentID` (`StudentID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`)
) ENGINE=InnoDB AUTO_INCREMENT=5302 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paymentaudit`
--

DROP TABLE IF EXISTS `paymentaudit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paymentaudit` (
  `AuditID` int NOT NULL AUTO_INCREMENT,
  `PaymentID` int NOT NULL,
  `AdminID` int NOT NULL,
  `Action` enum('Verified','Flagged','Adjusted','Refunded','Commented') NOT NULL,
  `Notes` text,
  `OccurredAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`AuditID`),
  KEY `PaymentID` (`PaymentID`),
  KEY `AdminID` (`AdminID`),
  CONSTRAINT `paymentaudit_ibfk_1` FOREIGN KEY (`PaymentID`) REFERENCES `payment` (`PaymentID`) ON DELETE CASCADE,
  CONSTRAINT `paymentaudit_ibfk_2` FOREIGN KEY (`AdminID`) REFERENCES `admin` (`AdminID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paymentdocument`
--

DROP TABLE IF EXISTS `paymentdocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paymentdocument` (
  `PaymentID` int NOT NULL,
  `DocumentID` int NOT NULL,
  PRIMARY KEY (`PaymentID`,`DocumentID`),
  KEY `DocumentID` (`DocumentID`),
  CONSTRAINT `paymentdocument_ibfk_1` FOREIGN KEY (`PaymentID`) REFERENCES `payment` (`PaymentID`) ON DELETE CASCADE,
  CONSTRAINT `paymentdocument_ibfk_2` FOREIGN KEY (`DocumentID`) REFERENCES `document` (`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `PersonID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `DOB` date DEFAULT NULL,
  `Gender` char(1) DEFAULT NULL,
  `Email` varchar(120) NOT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Password` varchar(255) NOT NULL,
  `Role` enum('Student','Faculty','Admin') NOT NULL,
  PRIMARY KEY (`PersonID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prerequisite`
--

DROP TABLE IF EXISTS `prerequisite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prerequisite` (
  `CourseID` int NOT NULL,
  `PrerequisiteCourseID` int NOT NULL,
  PRIMARY KEY (`CourseID`,`PrerequisiteCourseID`),
  KEY `PrerequisiteCourseID` (`PrerequisiteCourseID`),
  CONSTRAINT `prerequisite_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`),
  CONSTRAINT `prerequisite_ibfk_2` FOREIGN KEY (`PrerequisiteCourseID`) REFERENCES `course` (`CourseID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `program`
--

DROP TABLE IF EXISTS `program`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `program` (
  `ProgramID` int NOT NULL AUTO_INCREMENT,
  `ProgramCode` varchar(20) NOT NULL,
  `ProgramName` varchar(100) NOT NULL,
  `DepartmentID` int NOT NULL,
  PRIMARY KEY (`ProgramID`),
  UNIQUE KEY `ProgramCode` (`ProgramCode`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `program_ibfk_1` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `request`
--

DROP TABLE IF EXISTS `request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `request` (
  `RequestID` int NOT NULL AUTO_INCREMENT,
  `StudentID` int NOT NULL,
  `RequestType` enum('InfoUpdate','Certificate','IDReissue') NOT NULL,
  `RequestDate` datetime NOT NULL,
  `Status` enum('Pending','Approved','Rejected') NOT NULL,
  `ApprovedBy` int DEFAULT NULL,
  `ApprovedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`RequestID`),
  KEY `StudentID` (`StudentID`),
  KEY `ApprovedBy` (`ApprovedBy`),
  CONSTRAINT `request_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`),
  CONSTRAINT `request_ibfk_2` FOREIGN KEY (`ApprovedBy`) REFERENCES `admin` (`AdminID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `requestdocument`
--

DROP TABLE IF EXISTS `requestdocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requestdocument` (
  `RequestID` int NOT NULL,
  `DocumentID` int NOT NULL,
  PRIMARY KEY (`RequestID`,`DocumentID`),
  KEY `DocumentID` (`DocumentID`),
  CONSTRAINT `requestdocument_ibfk_1` FOREIGN KEY (`RequestID`) REFERENCES `request` (`RequestID`) ON DELETE CASCADE,
  CONSTRAINT `requestdocument_ibfk_2` FOREIGN KEY (`DocumentID`) REFERENCES `document` (`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `StudentID` int NOT NULL,
  `RollNo` varchar(30) NOT NULL,
  `ProgramID` int NOT NULL,
  `Semester` int NOT NULL,
  `AdmissionYear` int NOT NULL,
  PRIMARY KEY (`StudentID`),
  UNIQUE KEY `RollNo` (`RollNo`),
  KEY `ProgramID` (`ProgramID`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `person` (`PersonID`),
  CONSTRAINT `student_ibfk_2` FOREIGN KEY (`ProgramID`) REFERENCES `program` (`ProgramID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `submission`
--

DROP TABLE IF EXISTS `submission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submission` (
  `SubmissionID` int NOT NULL AUTO_INCREMENT,
  `AssignmentID` int NOT NULL,
  `StudentID` int NOT NULL,
  `SubmittedAt` datetime NOT NULL,
  `Marks` int DEFAULT NULL,
  `Comments` text,
  PRIMARY KEY (`SubmissionID`),
  UNIQUE KEY `AssignmentID` (`AssignmentID`,`StudentID`),
  KEY `StudentID` (`StudentID`),
  CONSTRAINT `submission_ibfk_1` FOREIGN KEY (`AssignmentID`) REFERENCES `assignment` (`AssignmentID`) ON DELETE CASCADE,
  CONSTRAINT `submission_ibfk_2` FOREIGN KEY (`StudentID`) REFERENCES `student` (`StudentID`)
) ENGINE=InnoDB AUTO_INCREMENT=6204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `submissiondocument`
--

DROP TABLE IF EXISTS `submissiondocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submissiondocument` (
  `SubmissionID` int NOT NULL,
  `DocumentID` int NOT NULL,
  PRIMARY KEY (`SubmissionID`,`DocumentID`),
  KEY `DocumentID` (`DocumentID`),
  CONSTRAINT `submissiondocument_ibfk_1` FOREIGN KEY (`SubmissionID`) REFERENCES `submission` (`SubmissionID`) ON DELETE CASCADE,
  CONSTRAINT `submissiondocument_ibfk_2` FOREIGN KEY (`DocumentID`) REFERENCES `document` (`DocumentID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `submissionevaluation`
--

DROP TABLE IF EXISTS `submissionevaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submissionevaluation` (
  `EvaluationID` int NOT NULL AUTO_INCREMENT,
  `SubmissionID` int NOT NULL,
  `FacultyID` int NOT NULL,
  `MarksGiven` int NOT NULL,
  `Comments` text,
  `EvaluatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`EvaluationID`),
  KEY `SubmissionID` (`SubmissionID`),
  KEY `FacultyID` (`FacultyID`),
  CONSTRAINT `submissionevaluation_ibfk_1` FOREIGN KEY (`SubmissionID`) REFERENCES `submission` (`SubmissionID`) ON DELETE CASCADE,
  CONSTRAINT `submissionevaluation_ibfk_2` FOREIGN KEY (`FacultyID`) REFERENCES `faculty` (`FacultyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teaches`
--

DROP TABLE IF EXISTS `teaches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teaches` (
  `FacultyID` int NOT NULL,
  `CourseID` int NOT NULL,
  PRIMARY KEY (`FacultyID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `teaches_ibfk_1` FOREIGN KEY (`FacultyID`) REFERENCES `faculty` (`FacultyID`),
  CONSTRAINT `teaches_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timetable`
--

DROP TABLE IF EXISTS `timetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable` (
  `TimetableID` int NOT NULL AUTO_INCREMENT,
  `CourseID` int NOT NULL,
  `DayOfWeek` enum('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
  `StartTime` time NOT NULL,
  `EndTime` time NOT NULL,
  `RoomNo` varchar(20) NOT NULL,
  `Type` enum('Lecture','Lab','Exam') NOT NULL,
  PRIMARY KEY (`TimetableID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `timetable_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `course` (`CourseID`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'student_management'
--

--
-- Dumping routines for database 'student_management'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-16 16:11:34
