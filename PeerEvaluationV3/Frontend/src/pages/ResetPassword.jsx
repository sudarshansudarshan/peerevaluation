import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

export default function ResetPassword() {
    const { token } = useParams();
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleReset = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        try {
            const res = await axios.post(`http://localhost:5000/api/auth/reset-password/${token}`, { password });
            setMessage(res.data.message);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError(err.response?.data?.message || 'Invalid or expired token');
        }
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            height: '100vh',
            width: '100vw',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%)',
            padding: '2rem',
            boxSizing: 'border-box',
        }}>
            <Link to="/" style={{
                position: 'absolute',
                top: 24,
                left: 24,
                background: '#fff',
                borderRadius: '50%',
                boxShadow: '0 2px 8px rgba(60,60,120,0.10)',
                width: 40,
                height: 40,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textDecoration: 'none'
            }} aria-label="Go to homepage">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <path d="M3 10.5L12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-5h-6v5H4a1 1 0 0 1-1-1V10.5z" stroke="#667eea" strokeWidth="2" strokeLinejoin="round" fill="none"/>
                </svg>
            </Link>

            <div style={{
                background: '#fff',
                padding: '2.5rem 2rem',
                borderRadius: '20px',
                boxShadow: '0 8px 32px rgba(60,60,120,0.12)',
                minWidth: '320px',
                maxWidth: '420px',
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '1.5rem',
            }}>
                <div style={{
                    width: 70,
                    height: 70,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '0.5rem',
                    boxShadow: '0 2px 12px rgba(102,126,234,0.18)'
                }}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="#fff">
                        <path d="M12 2a7 7 0 0 1 7 7v2h1a2 2 0 0 1 2 2v9H2v-9a2 2 0 0 1 2-2h1V9a7 7 0 0 1 7-7Zm0 2a5 5 0 0 0-5 5v2h10V9a5 5 0 0 0-5-5Z"/>
                    </svg>
                </div>

                <h1 style={{
                    textAlign: 'center',
                    color: '#3f3d56',
                    fontWeight: 700,
                    fontSize: '2rem',
                    marginBottom: '0.5rem'
                }}>Reset Password</h1>

                <form onSubmit={handleReset} style={{
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1.2rem',
                    marginTop: '1rem'
                }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label htmlFor="password" style={{
                            color: '#3f3d56',
                            fontWeight: 500,
                            fontSize: '1rem',
                        }}>New Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                padding: '0.75rem 1rem',
                                borderRadius: '8px',
                                border: '1px solid #c3cfe2',
                                background: '#f7f8fa',
                                fontSize: '1rem',
                                outline: 'none',
                                color: '#222'
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label htmlFor="confirmPassword" style={{
                            color: '#3f3d56',
                            fontWeight: 500,
                            fontSize: '1rem',
                        }}>Confirm Password</label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            style={{
                                padding: '0.75rem 1rem',
                                borderRadius: '8px',
                                border: '1px solid #c3cfe2',
                                background: '#f7f8fa',
                                fontSize: '1rem',
                                outline: 'none',
                                color: '#222'
                            }}
                        />
                    </div>

                    <button type="submit" style={{
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        border: 'none',
                        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                        color: '#fff',
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        cursor: 'pointer',
                        boxShadow: '0 2px 8px rgba(102,126,234,0.12)'
                    }}>
                        Reset Password
                    </button>

                    {message && <p style={{ color: 'green', textAlign: 'center', margin: 0 }}>{message}</p>}
                    {error && <p style={{ color: 'red', textAlign: 'center', margin: 0 }}>{error}</p>}
                </form>
            </div>
        </div>
    );
}
