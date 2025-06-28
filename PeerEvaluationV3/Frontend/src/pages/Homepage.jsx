import { useNavigate } from 'react-router-dom';

const iconButtonStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: 'none',
    borderRadius: '50%',
    padding: '24px',
    cursor: 'pointer',
    transition: 'background 0.2s, transform 0.15s',
    margin: '0 auto',
    boxShadow: '0 2px 8px rgba(102,126,234,0.12)',
};

const featureList = [
    {
        icon: (
            <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="#667eea" opacity="0.15"/>
                <path fill="#667eea" d="M12 7v5l4 2"/>
            </svg>
        ),
        title: "Track Progress",
        desc: "Monitor your evaluation status and feedback in real time."
    },
    {
        icon: (
            <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
                <rect width="20" height="20" x="2" y="2" rx="5" fill="#14b8a6" opacity="0.15"/>
                <path fill="#14b8a6" d="M7 12l3 3 7-7"/>
            </svg>
        ),
        title: "Easy Evaluation",
        desc: "Submit and review peer evaluations with a simple interface."
    },
    {
        icon: (
            <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
                <ellipse cx="12" cy="12" rx="10" ry="8" fill="#764ba2" opacity="0.15"/>
                <path fill="#764ba2" d="M8 12h8M12 8v8"/>
            </svg>
        ),
        title: "Secure & Private",
        desc: "Your data is encrypted and privacy is our top priority."
    }
];

const Homepage = () => {
    const navigate = useNavigate();

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            minHeight: '100vh',
            minWidth: '100vw',
            height: '100vh',
            width: '100vw',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%)',
            padding: '2rem',
            boxSizing: 'border-box',
            zIndex: 0
        }}>
            <div
                style={{
                    background: '#fff',
                    padding: '2.5rem 2rem',
                    borderRadius: '20px',
                    boxShadow: '0 8px 32px rgba(60,60,120,0.12)',
                    minWidth: '320px',
                    maxWidth: '440px',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '1.5rem',
                    border: 'none',
                    transition: 'box-shadow 0.2s',
                    textAlign: 'center',
                    position: 'relative',
                    overflow: 'hidden'
                }}
            >
                {/* Decorative gradient circle */}
                <div style={{
                    position: 'absolute',
                    top: -60,
                    right: -60,
                    width: 140,
                    height: 140,
                    background: 'radial-gradient(circle at 30% 30%, #667eea33 60%, transparent 100%)',
                    borderRadius: '50%',
                    zIndex: 0,
                }} />
                {/* Logo */}
                <div
                    style={{
                        width: 70,
                        height: 70,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '0.5rem',
                        boxShadow: '0 2px 12px rgba(102,126,234,0.18)',
                        zIndex: 1
                    }}
                >
                    <svg width="36" height="36" fill="none" viewBox="0 0 24 24">
                        <path fill="#fff" d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2c-3.33 0-10 1.67-10 5v3h20v-3c0-3.33-6.67-5-10-5Z"/>
                    </svg>
                </div>
                <h1 style={{
                    fontWeight: 700,
                    color: '#3f3d56',
                    fontSize: '2rem',
                    marginBottom: 8,
                    letterSpacing: '1px',
                    zIndex: 1
                }}>
                    Peer Evaluation System
                </h1>
                <div style={{ color: '#7a7a9d', fontSize: '1.1rem', marginBottom: 16, zIndex: 1 }}>
                    Welcome! Please login or register to continue.
                </div>
                {/* Features */}
                <div style={{
                    display: 'flex',
                    flexDirection: 'row',
                    gap: 16,
                    justifyContent: 'center',
                    margin: '12px 0 8px 0',
                    width: '100%',
                    zIndex: 1
                }}>
                    {featureList.map((f, i) => (
                        <div key={i} style={{
                            background: '#f6f8fc',
                            borderRadius: 12,
                            padding: '12px 10px',
                            minWidth: 0,
                            flex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            boxShadow: '0 1px 4px rgba(102,126,234,0.07)',
                            margin: '0 2px'
                        }}>
                            <div style={{ marginBottom: 6 }}>{f.icon}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.97rem', color: '#3f3d56', marginBottom: 2 }}>{f.title}</div>
                            <div style={{ fontSize: '0.85rem', color: '#7a7a9d' }}>{f.desc}</div>
                        </div>
                    ))}
                </div>
                {/* Buttons */}
                <div style={{ display: 'flex', flexDirection: 'row', gap: 48, justifyContent: 'center', marginTop: 32, zIndex: 1 }}>
                    <div>
                        <button
                            style={{
                                ...iconButtonStyle,
                                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                                color: '#fff',
                            }}
                            onClick={() => navigate('/login')}
                            onMouseOver={e => {
                                e.currentTarget.style.background = '#4f46e5';
                                e.currentTarget.style.transform = 'scale(1.07)';
                            }}
                            onMouseOut={e => {
                                e.currentTarget.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
                                e.currentTarget.style.transform = 'scale(1)';
                            }}
                            aria-label="Login"
                        >
                            <svg width="40" height="40" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59z"/>
                                <path d="M19 3H5c-1.1 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
                            </svg>
                        </button>
                        <div style={{ marginTop: 8, fontSize: '1rem', color: '#3f3d56', fontWeight: 500 }}>Login</div>
                    </div>
                    <div>
                        <button
                            style={{
                                ...iconButtonStyle,
                                background: 'linear-gradient(90deg, #14b8a6 0%, #06b6d4 100%)',
                                color: '#fff',
                            }}
                            onClick={() => navigate('/register')}
                            onMouseOver={e => {
                                e.currentTarget.style.background = '#0d9488';
                                e.currentTarget.style.transform = 'scale(1.07)';
                            }}
                            onMouseOut={e => {
                                e.currentTarget.style.background = 'linear-gradient(90deg, #14b8a6 0%, #06b6d4 100%)';
                                e.currentTarget.style.transform = 'scale(1)';
                            }}
                            aria-label="Register"
                        >
                            <svg width="40" height="40" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M15 12c2.7 0 8 1.34 8 4v4H7v-4c0-2.66 5.3-4 8-4zm0-2c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm-6 2v2H7v2h2v2h2v-2h2v-2h-2v-2h-2z"/>
                            </svg>
                        </button>
                        <div style={{ marginTop: 8, fontSize: '1rem', color: '#3f3d56', fontWeight: 500 }}>Register</div>
                    </div>
                </div>
            </div>
            <style>{`
                html, body {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    background: linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%);
                    min-height: 100vh;
                    min-width: 100vw;
                }
                @media (max-width: 600px) {
                    padding: 0;
                    box-sizing: border-box;
                    overflow: hidden;
                }
                @media (max-width: 600px) {
                    div[style*="background: #fff"] {
                        min-width: 95vw !important;
                        padding: 1.2rem 0.3rem !important;
                        border-radius: 12px !important;
                    }
                    h1 {
                        font-size: 1.3rem !important;
                    }
                    div[style*="display: flex"][style*="gap: 48px"] {
                        flex-direction: column !important;
                        gap: 1.5rem !important;
                    }
                    div[style*="display: flex"][style*="gap: 16px"] {
                        flex-direction: column !important;
                        gap: 0.7rem !important;
                    }
                }
                @media (min-width: 900px) {
                    div[style*="background: #fff"] {
                        min-width: 400px !important;
                        max-width: 480px !important;
                        padding: 3rem 2.5rem !important;
                    }
                }
            `}</style>
        </div>
    );
};

export default Homepage;