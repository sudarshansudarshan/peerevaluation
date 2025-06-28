import mongoose from 'mongoose';

const DocumentSchema = new mongoose.Schema({
  uniqueId: { type: String, required: true }, // Extracted from QR code
  examId: { type: mongoose.Schema.Types.ObjectId, ref: 'Examination', required: true },
  uploadedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  uploadedOn: { type: Date, default: Date.now },
  documentPath: { type: String, required: true }, // Path where the document is saved
});

export const Document = mongoose.model('Document', DocumentSchema);