import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import nodemailer from 'nodemailer';
import crypto from 'crypto';
import { User } from '../models/User.js';
import sendEmail from '../utils/sendEmail.js';
import { Course } from '../models/Course.js';
import emailExistence from 'email-existence';
import { Batch } from '../models/Batch.js';

// Generate JWT token
const generateToken = (id, role) => {
  return jwt.sign({ id, role }, process.env.JWT_SECRET || 'default_secret', {
    expiresIn: '30d'
  });
};

// Register User
export const registerUser = async (req, res) => {
  const { name, email, password, role } = req.body;

  try {
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'User already exists.' });
    }

    // Verify email existence
    const emailIsValid = await new Promise((resolve) => {
      emailExistence.check(email, (err, exists) => {
        if (err) resolve(false);
        else resolve(exists);
      });
    });

    if (!emailIsValid) {
      return res.status(400).json({ message: 'Email address does not exist or is invalid.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      email,
      password: hashedPassword,
      role,
    });

    // Send welcome email
    const welcomeHtml = `
      <div style="font-family:Arial,sans-serif; padding:20px;">
        <h2>Welcome to the Peer Evaluation System</h2>
        <p>Hi ${user.name},</p>
        <p>Thank you for registering on the <strong>Peer Evaluation System</strong>.</p>
        <p>Your account has been successfully created with the following details:</p>
        <ul>
          <li><strong>Email:</strong> ${user.email}</li>
          <li><strong>Role:</strong> ${user.role}</li>
        </ul>
        <p>We're excited to have you onboard!</p>
        <br/>
        <p>Best regards,<br/>PES Team</p>
      </div>
    `;

    await sendEmail(user.email, 'Welcome to Peer Evaluation System', welcomeHtml);

    res.status(201).json({
      _id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      token: generateToken(user._id, user.role),
    });
  } catch (error) {
    console.error('Registration error:', error.message);
    res.status(500).json({ message: error.message });
  }
};

// Login
export const loginUser = async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ message: 'User not found.' });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ message: 'Invalid credentials!' });

    res.status(200).json({
      _id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      token: generateToken(user._id, user.role)
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Protected Profile
export const getProfile = async (req, res) => {
  if (!req.user) return res.status(404).json({ message: 'User not found' });

  res.status(200).json({
    _id: req.user._id,
    name: req.user.name,
    email: req.user.email,
    role: req.user.role,
    isTA: req.user.isTA
  });
};

// Forgot Password
export const forgotPassword = async (req, res) => {
  const { email } = req.body;

  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: 'User not found' });

    const token = crypto.randomBytes(32).toString('hex');
    user.resetToken = token;
    user.tokenExpiry = Date.now() + 3600000; // 1 hour
    await user.save();

    // const resetLink = `http://localhost:3000/reset-password/${token}`;
    const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5000';
    const resetLink = `${CLIENT_URL}/reset-password/${token}`;
    const html = `
      <div style="font-family:Arial,sans-serif; padding:20px;">
        <h2>Password Reset Request</h2>
        <p>Hi ${user.name || ''},</p>
        <p>Click the button below to reset your password. This link will expire in 1 hour.</p>
        <a href="${resetLink}" style="background:#667eea;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Reset Password</a>
        <p>If you did not request a password reset, please ignore this email.</p>
      </div>
    `;

    const transporter = nodemailer.createTransport({
      service: 'Gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });
    // console.log("EMAIL_USER:", process.env.EMAIL_USER);
    // console.log("EMAIL_PASS:", process.env.EMAIL_PASS ? 'Loaded' : 'Missing');


    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: user.email,
      subject: 'Password Reset for Peer Evaluation System',
      html
    });

    res.status(200).json({ message: 'Reset link sent to your email.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};

// Reset Password
export const resetPassword = async (req, res) => {
  const { token } = req.params;
  const { password } = req.body;

  try {
    const user = await User.findOne({
      resetToken: token,
      tokenExpiry: { $gt: Date.now() }
    });

    if (!user) {
      return res.status(400).json({ message: 'Invalid or expired token' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    user.password = hashedPassword;
    user.resetToken = undefined;
    user.tokenExpiry = undefined;

    await user.save();

    res.status(200).json({ message: 'Password has been reset successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};

// Change Password
export const changePassword = async (req, res) => {
  const { currentPassword, newPassword } = req.body;

  try {
    const user = await User.findById(req.user._id);
    if (!user) return res.status(404).json({ message: 'User not found' });

    const isMatch = await bcrypt.compare(currentPassword, user.password);
    if (!isMatch) return res.status(400).json({ message: 'Current password is incorrect' });

    user.password = await bcrypt.hash(newPassword, 10);
    await user.save();

    res.status(200).json({ message: 'Password changed successfully' });
  } catch (error) {
    console.error('Change password error:', error.message);
    res.status(500).json({ message: 'Server error' });
  }
};

