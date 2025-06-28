import mongoose from 'mongoose';

const BatchSchema = new mongoose.Schema({
    batchId: { type: String, required: true },
    instructor: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    course: { type: mongoose.Schema.Types.ObjectId, ref: 'Course', required: true },
});

// Compound unique index on batchId and course
BatchSchema.index({ batchId: 1, course: 1 }, { unique: true });

// Automatically delete batches if the referenced course or instructor is removed
BatchSchema.pre('save', async function(next) {
    // No-op: this is just to ensure the schema is loaded before hooks are attached
    next();
});

BatchSchema.pre('findOneAndDelete', async function(next) {
  const batch = await this.model.findOne(this.getQuery());
  if (batch) {
    await mongoose.model('Enrollment').deleteMany({ batch: batch._id });
    await mongoose.model('Examination').deleteMany({ batch: batch._id });
  }
  next();
});

// Remove batches when a referenced course is deleted
mongoose.model('Course').schema.pre('findOneAndDelete', async function(next) {
    const doc = await this.model.findOne(this.getQuery());
    if (doc) {
        await mongoose.model('Batch').deleteMany({ course: doc._id });
    }
    next();
});

// Remove batches when a referenced instructor is deleted
mongoose.model('User').schema.pre('findOneAndDelete', async function(next) {
    const doc = await this.model.findOne(this.getQuery());
    if (doc) {
        await mongoose.model('Batch').deleteMany({ instructor: doc._id });
    }
    next();
});

export const Batch = mongoose.model('Batch', BatchSchema);
