import express from 'express';
import { getAllExamsForStudent, getAvailableCourses, getBatchesForCourse, getEnrolledBatches, getEnrolledCourses, getEvaluationsByBatchAndExam, getStudentDashboardStats, requestEnrollment, uploadExamDocument } from '../controllers/studentController.js';
import { protect } from '../middleware/authMiddleware.js';
import upload from '../utils/fileUpload.js';

const router = express.Router();

router.get('/dashboard-stats', protect, getStudentDashboardStats);
router.get('/enrolled-courses', protect, getEnrolledCourses);
router.get('/available-courses', protect, getAvailableCourses);
router.get('/course-batches/:courseId', protect, getBatchesForCourse);
router.post('/request-enrollment', protect, requestEnrollment);
router.get('/enrolled-batches', protect, getEnrolledBatches);
router.get('/all-exams', protect, getAllExamsForStudent);
router.post('/upload-exam-document', protect, upload.single('file'), uploadExamDocument);
router.get('/evaluations', protect, getEvaluationsByBatchAndExam);

export default router;