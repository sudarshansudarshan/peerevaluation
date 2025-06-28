import { User } from '../models/User.js';
import { Enrollment } from '../models/Enrollment.js';
import { Examination } from '../models/Examination.js';
import { Document } from '../models/Document.js';
import { Batch } from '../models/Batch.js';
import { Course } from '../models/Course.js';
import { UIDMap } from '../models/UIDMap.js';
import { TA } from '../models/TA.js';


export const getMyTABatches = async (req, res) => {
  try {
    const taUserId = req.user._id;

    const taAssignments = await TA.find({ userId: taUserId });
    if (!taAssignments.length) {
      return res.status(404).json({ message: 'No batch assigned to you as TA.' });
    }

    const results = await Promise.all(
      taAssignments.map(async (ta) => {
        const batch = await Batch.findById(ta.batch);
        if (!batch) return null;
        const course = await Course.findById(batch.course);
        const instructor = await User.findById(batch.instructor);

        return {
          courseName: course?.courseName || '',
          courseId: course?.courseId || '',
          batchId: batch.batchId,
          instructorName: instructor?.name || '',
        };
      })
    );

    // Filter out any nulls (in case of missing batch/course/instructor)
    const filteredResults = results.filter(Boolean);

    if (!filteredResults.length) {
      return res.status(404).json({ message: 'No valid batch assignments found.' });
    }

    res.json(filteredResults);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch TA batch info.' });
  }
};