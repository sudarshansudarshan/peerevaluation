import express from 'express';
import { updateRole, addCourse, getTeachers, getCourses, addBatch, getDashboardCounts, deleteCourse, getBatches, deleteBatch } from '../controllers/adminController.js';
import { protect, adminOrTeacherOnly } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/update-role', protect, adminOrTeacherOnly, updateRole);
router.post('/add-course', protect, addCourse);
router.get('/teachers', protect, getTeachers);
router.get('/courses', protect, getCourses);
router.get('/batches', protect, getBatches);
router.post('/add-batch', protect, addBatch);
router.get('/dashboard-counts', protect, getDashboardCounts);
router.delete('/delete-course/:courseId', protect, adminOrTeacherOnly, deleteCourse);
router.delete('/delete-batch/:batchId', protect, adminOrTeacherOnly, deleteBatch);

export default router;


// update the whole routes in the admin and teacher dashboard and also add it to server.js