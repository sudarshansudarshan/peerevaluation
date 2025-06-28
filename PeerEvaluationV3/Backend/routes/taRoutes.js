import express from 'express';
import { protect } from '../middleware/authMiddleware.js';
import upload from '../utils/fileUpload.js';
import { getMyTABatches } from '../controllers/taController.js';

const router = express.Router();

router.get('/my-batches', protect, getMyTABatches);

export default router;