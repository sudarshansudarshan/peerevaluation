import express from 'express';
import { protect, adminOrTeacherOnly } from '../middleware/authMiddleware.js';
import { assignTA, bulkUploadDocuments, completeExam, deassignTA, deleteExam, downloadPDF, flagEvaluations, getEnrolledStudents, getExamsForTeacher, getTeacherCoursesAndBatches, scheduleExam, sendEvaluation, studentsEnroll, updateExam } from '../controllers/teacherController.js';
// import multer from 'multer';
import upload from '../utils/fileUpload.js'; // Assuming you have a fileUpload.js for handling file uploads

const router = express.Router();
// const upload = multer({ dest: 'uploads/' });

router.post('/assign-ta', protect, adminOrTeacherOnly, assignTA);
router.post('/deassign-ta', protect, adminOrTeacherOnly, deassignTA);
router.get('/teacher-courses-batches', protect, adminOrTeacherOnly, getTeacherCoursesAndBatches);
router.post('/students-enroll', protect, adminOrTeacherOnly, upload.single('file'), studentsEnroll);
router.get('/enrolled-students', protect, adminOrTeacherOnly, getEnrolledStudents);
router.post('/exam-schedule', protect, adminOrTeacherOnly, upload.single('solutions'), scheduleExam);
router.get('/teacher-exams', protect, adminOrTeacherOnly, getExamsForTeacher);
router.put('/update-exam/:id', protect, adminOrTeacherOnly, upload.single('solutions'), updateExam);
router.get('/download-pdf/:examId', protect, adminOrTeacherOnly, downloadPDF);
router.post('/bulk-upload', protect, adminOrTeacherOnly, upload.array('documents'), bulkUploadDocuments);
router.post('/send-evaluation/:examId', protect, adminOrTeacherOnly, sendEvaluation);
router.post('/flag-evaluations/:examId', protect, adminOrTeacherOnly, flagEvaluations);
router.put('/mark-exam-done/:examId', protect, adminOrTeacherOnly, completeExam);
router.delete('/delete-exam/:id', protect, adminOrTeacherOnly, deleteExam);

export default router;