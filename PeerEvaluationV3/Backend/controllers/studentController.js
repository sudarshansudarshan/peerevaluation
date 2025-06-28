import { User } from '../models/User.js';
import { Enrollment } from '../models/Enrollment.js';
import { Examination } from '../models/Examination.js';
import { Document } from '../models/Document.js';
import { Batch } from '../models/Batch.js';
import { Course } from '../models/Course.js';
import { UIDMap } from '../models/UIDMap.js';
import fs from 'fs';

export const getStudentDashboardStats = async (req, res) => {
//   console.log('Fetching student dashboard stats for user:', req.user._id);
  try {
    const studentId = req.user._id;

    const coursesEnrolled = await Enrollment.countDocuments({ student: studentId , status: 'active' });

    const pendingEvaluations = await Document.countDocuments({
      uniqueId: studentId,
      evaluationStatus: 'pending'
    });

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    // Get all not-completed exams for today
    const todaysExams = await Examination.find({
      completed: false,
      date: { $gte: today, $lt: tomorrow }
    });

    let activeExams = 0;
    const now = new Date();

    todaysExams.forEach(exam => {
      // exam.time is "HH:MM"
      const [startHour, startMinute] = exam.time.split(':').map(Number);
      const examStart = new Date(exam.date);
      examStart.setHours(startHour, startMinute, 0, 0);

      const examEnd = new Date(examStart.getTime() + exam.duration * 60000);

      if (now >= examStart && now < examEnd) {
        activeExams += 1;
      }
    });

    res.json({
      coursesEnrolled,
      pendingEvaluations,
      activeExams
    });
  } catch (error) {
    console.error('Error fetching student dashboard stats:', error);
    res.status(500).json({ message: 'Failed to fetch dashboard stats' });
  }
};

export const getEnrolledCourses = async (req, res) => {
  try {
    const studentId = req.user._id;

    const enrollments = await Enrollment.find({ student: studentId, status: 'active' })
      .populate({
        path: 'course',
        select: 'courseName'
      })
      .populate({
        path: 'batch',
        select: 'batchId'
      });

    // Format the response
    const result = enrollments.map(enrollment => ({
      courseName: enrollment.course?.courseName || 'Unknown Course',
      batchName: enrollment.batch?.batchId || 'Unknown Batch'
    }));

    res.json(result);
  } catch (error) {
    console.error('Error fetching enrolled courses:', error);
    res.status(500).json({ message: 'Failed to fetch enrolled courses' });
  }
};

export const getAvailableCourses = async (req, res) => {
  try {
    const courses = await Course.find({});
    res.json(courses);
  } catch (error) {
    console.error('Error fetching available courses:', error);
    res.status(500).json({ message: 'Failed to fetch available courses' });
  }
};

export const getBatchesForCourse = async (req, res) => {
  try {
    const { courseId } = req.params;
    const batches = await Batch.find({ course: courseId });
    res.json(batches);
  } catch (error) {
    console.error('Error fetching batches for course:', error);
    res.status(500).json({ message: 'Failed to fetch batches for course' });
  }
};

export const requestEnrollment = async (req, res) => {
  try {
    const { courseId, batchId } = req.body;
    const studentId = req.user._id;

    const existingEnrollment = await Enrollment.findOne({
      student: studentId,
      batch: batchId,
      course: courseId,
      status: { $in: ['pending', 'active'] }
    });

    if (existingEnrollment && existingEnrollment.status === 'active') {
      return res.status(400).json({ message: 'Already enrolled in this course!' });
    }
    else if (existingEnrollment && existingEnrollment.status === 'pending') {
      return res.status(400).json({ message: 'You have a pending enrollment request for this course!' });
    }

    const newEnrollment = new Enrollment({
      student: studentId,
      course: courseId,
      batch: batchId,
      status: 'pending'
    });

    await newEnrollment.save();
    res.status(200).json({ message: 'Enrollment request submitted successfully!' });
  } catch (error) {
    console.error('Error requesting enrollment:', error);
    res.status(500).json({ message: 'Failed to request enrollment!' });
  }
};

export const getEnrolledBatches = async (req, res) => {
  try {
    const studentId = req.user._id;
    const enrollments = await Enrollment.find({ student: studentId, status: 'active' })
      .populate('batch')
      .populate('course');
    const result = enrollments.map(e => ({
      _id: e.batch._id,
      batchId: e.batch.batchId,
      courseName: e.course.courseName,
      courseId: e.course._id,
    }));
    res.json(result);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch batches' });
  }
};

export const getAllExamsForStudent = async (req, res) => {
  try {
    const studentId = req.user._id;
    const { batchId } = req.query;
    let batchFilter = {};
    if (batchId) batchFilter = { batch: batchId };
    const enrollments = await Enrollment.find({ student: studentId, status: 'active' });
    const batchIds = enrollments.map(e => e.batch);
    const filter = batchId ? { batch: batchId } : { batch: { $in: batchIds } };
    filter.completed = false;
    const exams = await Examination.find(filter);
    res.json(exams);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch exams' });
  }
};

export const uploadExamDocument = async (req, res) => {
  let messages = '';
  try {
    const { examId } = req.body;
    const studentId = req.user._id;
    const file = req.file;
    if (!file) return res.status(400).json({ message: 'No file found for Upload!' });

    // Find the uniqueId from UIDMap
    let uidMap = await UIDMap.findOne({ userId: studentId, examId });
    if (!uidMap) {
      // const uniqueId = await extractUserIdFromQR(file.path);
      // if (!uniqueId) {
      //   uniqueId = studentId;
      // }
      uidMap = await UIDMap.create({ uniqueId: studentId, userId: studentId, examId });
    }

    const existingDoc = await Document.findOne({
      uniqueId: uidMap.uniqueId,
      examId: examId
    });

    if (existingDoc && existingDoc.uploadedBy.toString() === studentId.toString()) {
      if (existingDoc.documentPath && fs.existsSync(existingDoc.documentPath)) {
        try {
          fs.unlinkSync(existingDoc.documentPath);
        } catch (err) {
          console.warn('Failed to delete old document file:', err);
        }
      }
      existingDoc.documentPath = file.path;
      existingDoc.uploadedBy = studentId;
      existingDoc.uploadedOn = new Date();
      await existingDoc.save();
      return res.status(200).json({ message: 'Existing document updated successfully!' });
    }
    else if (existingDoc && existingDoc.uploadedBy.toString() !== studentId.toString()) {
      const uploadedByUser = await User.findById(existingDoc.uploadedBy);
      if (uploadedByUser && uploadedByUser.role === 'teacher') {
        messages = `Teacher ${uploadedByUser.name} has already uploaded a document for this exam.`;
      }
      else {
        messages = `${uploadedByUser.name} has already uploaded a document for you for this exam.`;
      }
      try {
        fs.unlinkSync(file.path);
      } catch (err) {
        console.warn('Failed to delete new document file:', err);
      }
      return res.status(409).json({ message: messages });
    }
    else {
      await Document.create({
        uniqueId: uidMap.uniqueId,
        examId,
        documentPath: file.path,
        uploadedBy: studentId,
        uploadedOn: new Date(),
      });
      // await newDoc.save();
    }
    res.status(200).json({ message: 'File uploaded successfully!' });
  } catch (err) {
    try {
      fs.unlinkSync(req.file.path);
    } catch (err) {
      console.warn('Failed to delete new document file:', err);
    }
    res.status(500).json({ message: 'Failed to upload document!' });
  }
};