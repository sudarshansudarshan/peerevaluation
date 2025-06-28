import mongoose from 'mongoose';
// This code defines a Mongoose schema for a Course model in a Node.js application.

const CourseSchema = new mongoose.Schema({
    courseId: { type: String, required: true, unique: true },
    courseName: { type: String, required: true },
    openCourse: { type: Boolean, default: false },
    startDate: { type: Date },
    endDate: { type: Date },
    // enrolledStudents: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
});

export const Course = mongoose.model('Course', CourseSchema);
