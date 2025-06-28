import { Batch } from '../models/Batch.js';
import { Course } from '../models/Course.js';
import { User } from '../models/User.js';
import { Enrollment } from '../models/Enrollment.js';
import { Examination } from '../models/Examination.js';
import { Document } from '../models/Document.js';
import { UIDMap } from '../models/UIDMap.js';
import { TA } from '../models/TA.js';
import csv from 'csv-parser';
import fs from 'fs';
import bcrypt from 'bcryptjs';
import sendEmail from '../utils/sendEmail.js';
import extractUserIdFromQR from '../utils/extractUserIdFromQR.js'; 
import emailExistence from 'email-existence';
import { Parser } from 'json2csv';
import PDFDocument from 'pdfkit';
import QRCode from 'qrcode';
import mongoose from 'mongoose';


export const assignTA = async (req, res) => {
  try {
    const { email, batchId } = req.body;

    if (!email || !batchId) {
      return res.status(400).json({ message: 'Email and batchId are required.' });
    }

    const user = await User.findOne({ email, role: 'student' });
    if (!user) {
      return res.status(404).json({ message: 'Student with this email not found.' });
    }

    const batch = await Batch.findById(batchId);
    if (!batch) {
      return res.status(404).json({ message: 'Batch not found.' });
    }

    const isEnrolled = await Enrollment.exists({ student: user._id, batch: batch._id });
    if (isEnrolled) {
      return res.status(400).json({ message: 'Student is enrolled in this batch and cannot be assigned as TA.' });
    }

    const isAlreadyTA = await TA.exists({ userId: user._id, batch: batch._id });
    if (isAlreadyTA) {
      return res.status(409).json({ message: 'This user is already assigned as TA for the selected batch.' });
    }

    user.isTA = true;
    await user.save();

    await TA.create({
      userId: user._id,
      batch: batch._id
    });

    return res.status(200).json({ message: 'TA assigned to batch successfully.' });
  } catch (err) {
    console.error('Error assigning TA:', err);
    return res.status(500).json({ message: 'Failed to assign TA.', error: err.message });
  }
};

export const deassignTA = async (req, res) => {
  try {
    const { email, batchId } = req.body;

    if (!email || !batchId) {
      return res.status(400).json({ message: 'Email and batchId are required.' });
    }

    const user = await User.findOne({ email, role: 'student', isTA: true });
    if (!user) {
      return res.status(404).json({ message: 'TA not found with this email.' });
    }

    const batch = await Batch.findById(batchId);
    if (!batch) {
      return res.status(404).json({ message: 'Batch not found.' });
    }

    const taAssignment = await TA.findOne({ userId: user._id, batch: batch._id });
    if (!taAssignment) {
      return res.status(409).json({ message: 'TA is not assigned to this batch.' });
    }

    await TA.deleteOne({ _id: taAssignment._id });

    const stillTA = await TA.exists({ userId: user._id });
    if (!stillTA) {
      user.isTA = false;
      await user.save();
    }

    return res.status(200).json({ message: 'TA deassigned from batch successfully.' });
  } catch (err) {
    console.error('Error deassigning TA:', err);
    return res.status(500).json({ message: 'Failed to deassign TA.', error: err.message });
  }
};

function generateStrongPassword() {
  const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lower = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  const special = '!@#$%^&*()_+-=[]{}|;:,.<>?';
  const all = upper + lower + numbers + special;

  let password = '';
  password += upper[Math.floor(Math.random() * upper.length)];
  password += lower[Math.floor(Math.random() * lower.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += special[Math.floor(Math.random() * special.length)];

  for (let i = 4; i < 8; i++) {
  password += all[Math.floor(Math.random() * all.length)];
  }

  // Shuffle password to avoid predictable order
  return password.split('').sort(() => 0.5 - Math.random()).join('');
}

export const getTeacherCoursesAndBatches = async (req, res) => {
  try {
    const teacherId = req.user._id; // Assuming authentication middleware sets req.user
    // console.log('Fetching batches and courses for teacher ID:', teacherId);

    // Find all batches assigned to this teacher and populate the course field
    const batches = await Batch.find({ instructor: teacherId }).populate('course');

    if (!batches || batches.length === 0) {
      return res.status(404).json({ message: 'No batches found for this teacher.' });
    }

    // Structure: courseId => { name, batches: [] }
    const courseMap = {};

    batches.forEach(batch => {
      const course = batch.course;
      if (!courseMap[course._id]) {
        courseMap[course._id] = {
          id: course._id,
          name: course.courseName,
          batches: [],
        };
      }
      courseMap[course._id].batches.push({
        id: batch._id,
        name: batch.batchId, // You can also use `batchName` if available
      });
    });

    const result = Object.values(courseMap);

    res.status(200).json(result);
  } catch (error) {
    console.error('Error fetching batches and courses for teacher:', error);
    res.status(500).json({ message: 'Server error. Please try again later.' });
  }
};

export const studentsEnroll = async (req, res) => {
  let enrolled = 0, pending_enrollment = 0, new_enrollment = 0;
  try {
    const { course, batch } = req.body;
    const csvFile = req.file.path;

    if (!course || !batch || !csvFile) {
      return res.status(400).json({ message: 'Course, batch, and CSV file are required.' });
    }

    const students = [];

    fs.createReadStream(csvFile)
    .pipe(csv({
      mapHeaders: ({ header }) => header.trim().toLowerCase(), // normalize
    }))
    .on('data', (row) => {
      if (!row.name || !row.email) {
        console.error('Missing name or email in row:', row);
        return; // Skip rows with missing data
      }
      students.push({
        name: row.name,
        email: row.email.trim(), // Normalize email
      });
    })
    .on('end', async () => {
        for (const student of students) {
          if (!student.name || !student.email) {
            return res.status(400).json({ message: `Missing name or email for one of the student.` });
          }

          const emailIsValid = await new Promise((resolve) => {
            emailExistence.check(student.email, (err, exists) => {
              if (err) resolve(false);
              else resolve(exists);
            });
          });
      
          if (!emailIsValid) {
            return res.status(400).json({ message: 'Email address does not exist or is invalid for one of the student.' });
          }

          let user = await User.findOne({ email: student.email });

          if (!user) {
            const randomPassword = generateStrongPassword();
            const hashedPassword = await bcrypt.hash(randomPassword, 10);

            user = new User({
              name: student.name,
              email: student.email,
              password: hashedPassword,
              role: 'student',
            });

            // await user.save();

            // Send welcome email
            const htmlcontent = `
            <div style="font-family:Arial,sans-serif; padding:20px;">
              <h2>Welcome to the Peer Evaluation System</h2>
              <p>Hello ${student.name},</p>
              <p>Your account has been successfully created with the following details:</p>
              <ul>
                <li><strong>Email:</strong> ${student.email}</li>
                <li><strong>Password:</strong> ${randomPassword}</li>
              </ul>
              <p>We're excited to have you onboard!</p>
              <p>Please log in and change your password.</p>
              <br/>
              <p>Best regards,<br/>PES Team</p>
            </div>
            `;
            await sendEmail(
              student.email,
              'Welcome to Peer Evaluation System',
              htmlcontent
            );
            await user.save();
          }

          // Check if the student is already enrolled in the course and batch
          const existingEnrollment = await Enrollment.findOne({ student: user._id, course, batch });
          if (existingEnrollment && existingEnrollment.status === 'active') {
            // Fetch batch and course details to get their names/ids
            const batchDoc = await Batch.findById(batch);
            const courseDoc = await Course.findById(course);
            const batchName = batchDoc ? batchDoc.batchId : batch;
            const courseName = courseDoc ? courseDoc.courseName : course;
            enrolled++;
            // console.error(`Student ${student.name} is already enrolled in the batch ${batchName} of course ${courseName}.`);
            // return res.status(409).json({ message: `Student ${student.name} is already enrolled in the batch ${batchName} of course ${courseName}.` });
            continue;
          }
          else if (existingEnrollment && existingEnrollment.status === 'pending') {
            existingEnrollment.status = 'active';
            await existingEnrollment.save();
            pending_enrollment++;
            // return res.status(409).json({message: 'Students enrolled by accepting the pending enrollment request.'});
            // console.log(`Student ${student.name} already has a pending enrollment request, now activated.`);
          }
          else{
            const enrollment = new Enrollment({
              student: user._id,
              course,
              batch,
            });

            await enrollment.save();
            new_enrollment++;
          }
        }

        fs.unlink(csvFile, (err) => {
          if (err) {
            console.error('Error deleting uploaded CSV file:', err);
          }
        });

        res.status(200).json({ message: 'Students enrolled successfully', statistics: { enrolled, pending_enrollment, new_enrollment } });
      });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'An error occurred while enrolling students.' });
  }
};

export const getEnrolledStudents = async (req, res) => {
  try {
    const { courseId, batchId } = req.query;

    if (!courseId || !batchId) {
      return res.status(400).json({ message: 'Course ID and Batch ID are required.' });
    }

    const enrollments = await Enrollment.find({ course: courseId, batch: batchId, status: 'active' }).populate('student').populate('course').populate('batch');

    if (!enrollments || enrollments.length === 0) {
      return res.status(404).json({ message: 'No students found for the specified batch and course.' });
    }

    const students = enrollments.map(enrollment => ({
      name: enrollment.student.name,
      email: enrollment.student.email,
      enrollmentDate: enrollment.enrollmentDate ? new Date(enrollment.enrollmentDate).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) : 'N/A',
      batchName: enrollment.batch.batchId, // Assuming batchId is the identifier for the batch
      courseName: enrollment.course.courseName, // Assuming courseName is the identifier for the course
    }));

    const json2csvParser = new Parser();
    const csv = json2csvParser.parse(students);

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=students_${batchId}_${courseId}.csv`);
    res.status(200).send(csv);
  } catch (error) {
    console.error('Error fetching enrolled students:', error);
    res.status(500).json({ message: 'An error occurred while fetching enrolled students.' });
  }
};

export const scheduleExam = async (req, res) => {
  try {
    const { name, batch, date, time, number_of_questions, duration, totalMarks, k } = req.body;
    const solutions = req.file ? req.file.path : null;

    if (!name || !batch || !date || !time || !number_of_questions || !duration || !totalMarks || !k) {
      return res.status(400).json({ message: 'All fields are required.' });
    }

    const exam = new Examination({
      name,
      batch,
      date,
      time,
      number_of_questions,
      duration,
      totalMarks,
      k,
      solutions: solutions || '', // Optional field, can be empty
      total_students: 0, // This will be updated later
      createdBy: req.user._id, // Assuming req.user is set by auth middleware
    });

    await exam.save();

    res.status(201).json({ message: 'Exam scheduled successfully.', exam });
  } catch (error) {
    console.error('Error scheduling exam:', error);
    res.status(500).json({ message: 'An error occurred while scheduling the exam.' });
  }
};

export const getExamsForTeacher = async (req, res) => {
  try {
    const teacherId = req.user._id; // Assuming req.user contains the authenticated teacher's info
    const examss = await Examination.find({ createdBy: teacherId, completed: false })
      .populate({
      path: 'batch',
      select: 'batchId'
      })
      .lean();

    // Map exams to include only batchId in batch field
    const exams = examss.map(exam => ({
      ...exam,
      batch: exam.batch ? exam.batch.batchId : null
    }));

    res.status(200).json({ exams });
  } catch (error) {
    console.error('Error fetching exams:', error);
    res.status(500).json({ message: 'Failed to fetch exams' });
  }
};

export const updateExam = async (req, res) => {
  try {
    const examId = req.params.id;
    const { name, date, time, number_of_questions, duration, totalMarks, k, total_students } = req.body;
    const solutions = req.file ? req.file.path : null;

    // Find the exam first
    const exam = await Examination.findById(examId);

    if (!exam) {
      return res.status(404).json({ message: 'Exam not found' });
    }

    // Update exam details
    exam.name = name || exam.name;
    exam.date = date || exam.date;
    exam.time = time || exam.time;
    exam.number_of_questions = number_of_questions || exam.number_of_questions;
    exam.duration = duration || exam.duration;
    exam.totalMarks = totalMarks || exam.totalMarks;
    exam.k = k || exam.k;
    exam.total_students = total_students || exam.total_students;

    // Update solutions file if provided
    if (solutions) {
      // Delete old solutions file if it exists
      if (exam.solutions && typeof exam.solutions === 'string' && exam.solutions.trim() !== '') {
        fs.unlink(exam.solutions, (err) => {
          if (err && err.code !== 'ENOENT') {
            console.error('Error deleting old solutions file:', err);
          }
        });
      }
      exam.solutions = solutions;
    }

    await exam.save();

    res.status(200).json({ message: 'Exam updated successfully', exam });
  } catch (error) {
    console.error('Error updating exam:', error);
    res.status(500).json({ message: 'Failed to update exam' });
  }
};

export const completeExam = async (req, res) => {
  try {
    const { examId } = req.params;

    const exam = await Examination.findById(examId);

    if (!exam) {
      return res.status(404).json({ message: 'Exam not found' });
    }

    exam.completed = true;
    await exam.save();

    res.status(200).json({ message: 'Exam marked as completed successfully!' });
  } catch (error) {
    // console.error('Error marking exam as completed:', error);
    res.status(500).json({ message: 'Failed to mark exam as completed!' });
  }
}

export const deleteExam = async (req, res) => {
  try {
    const examId = req.params.id;

    // Find the exam first
    const exam = await Examination.findById(examId);

    if (!exam) {
      return res.status(404).json({ message: 'Exam not found' });
    }
    

    // Delete the associated file if it exists
    if (exam.solutions && typeof exam.solutions === 'string' && exam.solutions.trim() !== '') {
      fs.unlink(exam.solutions, (err) => {
        if (err && err.code !== 'ENOENT') {
          console.error('Error deleting solutions file:', err);
        }
      });
    }

    // Delete associated uploaded documents
    const documents = await Document.find({ examId });
    for (const doc of documents) {
      if (doc.documentPath && typeof doc.documentPath === 'string') {
        fs.unlink(doc.documentPath, (err) => {
          if (err && err.code !== 'ENOENT') {
            console.error('Error deleting uploaded document:', err);
          }
        });
      }
    }
    await Document.deleteMany({ examId });

    await UIDMap.deleteMany({ examId });

    // Delete the exam document
    await Examination.findByIdAndDelete(examId);

    res.status(200).json({ message: 'Exam deleted successfully' });
  } catch (error) {
    console.error('Error deleting exam:', error);
    res.status(500).json({ message: 'Failed to delete exam' });
  }
};

export const downloadPDF = async (req, res) => {
  const { examId } = req.params;

  try {
    const exam = await Examination.findById(examId);
    if (!exam) {
      return res.status(404).json({ message: 'Exam not found.' });
    }
    const batchId = exam.batch;

    const enrollments = await Enrollment.find({ batch: batchId }).populate('student');
    if (!enrollments.length) {
      return res.status(404).json({ message: 'No students enrolled for this batch.' });
    }

    const doc = new PDFDocument();
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=Exam_${examId}_QR_Codes.pdf`);

    doc.pipe(res);

    for (const enrollment of enrollments) {
      const userId = enrollment.student._id; 

      let uidMapEntry = await UIDMap.findOne({ userId, examId });
      let uniqueId;

      if (uidMapEntry) {
        uniqueId = uidMapEntry.uniqueId;
      } else {
        uniqueId = new mongoose.Types.ObjectId().toString(); 

        try {
          uidMapEntry = await UIDMap.create({ uniqueId, userId, examId });
        } catch (error) {
          if (error.code === 11000) {
            continue; 
          } else {
            return res.status(500).json({ message: 'Failed to create UIDMap entry.' });
          }
        }
      }

      // Generate QR code
      const qrCodeData = await QRCode.toDataURL(uniqueId);

      // Add a new page to the PDF
      // doc.addPage();
      doc.image(qrCodeData, { fit: [100, 100], align: 'center' });
      doc.text(`User ID: ${enrollment.student.email}`, { align: 'center' });
      doc.text(`User Name: ${enrollment.student.name}`, { align: 'center' });
      doc.addPage();
      doc.image(qrCodeData, { fit: [100, 100], align: 'center' });
      doc.addPage();
      
    }

    doc.end();
  } catch (error) {
    res.status(500).json({ message: 'Error generating PDF' });

    if (!res.headersSent) {
      res.status(500).json({ message: 'Failed to generate PDF' });
    }
  }
};

export const bulkUploadDocuments = async (req, res) => {
  try {
    const { examId } = req.body; 
    const uploadedBy = req.user._id;
    const files = req.files;

    let added = 0;
    let updated = 0;

    for (const file of files) {
      const uniqueId = await extractUserIdFromQR(file.path);
      if (!uniqueId) continue;
      const isUIDValid = await UIDMap.exists({ uniqueId, examId });
      if (!isUIDValid) {
        // console.warn(`Unique ID ${uniqueId} not found for exam ${examId}. Skipping file: ${file.originalname}`);
        continue;
      }
      const existingDoc = await Document.findOne({ uniqueId, examId });
      if (existingDoc) {
        if (existingDoc.documentPath && fs.existsSync(existingDoc.documentPath)) {
          try {
            fs.unlinkSync(existingDoc.documentPath);
          } catch (err) {
            console.warn('Failed to delete old document file:', err);
          }
        }
        existingDoc.documentPath = file.path;
        existingDoc.uploadedBy = uploadedBy;
        existingDoc.uploadedOn = new Date();
        await existingDoc.save();
        updated++;
      } else {
        // Create a new document
        await Document.create({
          uniqueId,
          examId,
          uploadedBy,
          documentPath: file.path,
        });
        added++;
      }
    }

    res.status(200).json({ message: 'Documents processed successfully', added, updated });
  } catch (error) {
    // console.error('Error during bulk upload:', error);
    res.status(500).json({ message: 'Failed to upload documents' });
  }
};

// TODO: Implement the logic to send evaluations to students
export const sendEvaluation = async (req, res) => {
  const { examId } = req.params;

  if (!examId) {
    return res.status(400).json({ message: 'Exam ID is required' });
  }

  try {
    // Replace with actual evaluation logic
    res.status(200).json({ message: 'Evaluation sent successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Failed to send evaluation' });
  }
};