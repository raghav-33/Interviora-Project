import { useState } from "react";
import Interview from "./Interview";

function JDInput() {
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState(null);

  const startInterview = async () => {
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/start-interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description: jd })
    });

    const data = await res.json();
    setSessionData(data);
    setLoading(false);
  };

  if (sessionData) {
    return (
      <Interview
        sessionId={sessionData.session_id}
        questions={sessionData.questions}
      />
    );
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h1 style={styles.title}>Interviora</h1>
        <p style={styles.subtitle}>
          Practice interviews powered by AI
        </p>

        <textarea
          placeholder="Paste Job Description here..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          style={styles.textarea}
        />

        <button onClick={startInterview} style={styles.button}>
          {loading ? "Preparing Questions..." : "Start Interview"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    width: "100%",
    display: "flex",
    justifyContent: "center",
  },

  card: {
    background: "rgba(30, 41, 59, 0.6)",
    backdropFilter: "blur(20px)",
    padding: "50px",
    borderRadius: "24px",
    width: "600px",
    boxShadow: "0 0 80px rgba(99,102,241,0.3)",
    border: "1px solid rgba(255,255,255,0.1)"
  },

  title: {
    fontSize: "42px",
    fontWeight: "800",
    background: "linear-gradient(90deg, #6366f1, #8b5cf6)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    marginBottom: "10px",
    textAlign: "center"
  },

  subtitle: {
    color: "#94a3b8",
    marginBottom: "30px",
    textAlign: "center"
  },

  textarea: {
    width: "100%",
    height: "150px",
    padding: "18px",
    borderRadius: "16px",
    border: "1px solid rgba(255,255,255,0.1)",
    background: "rgba(15, 23, 42, 0.8)",
    color: "white",
    marginBottom: "25px",
    fontSize: "15px",
    outline: "none"
  },

  button: {
    width: "100%",
    padding: "16px",
    borderRadius: "16px",
    border: "none",
    fontSize: "16px",
    fontWeight: "600",
    background: "linear-gradient(90deg, #6366f1, #8b5cf6)",
    color: "white",
    cursor: "pointer",
    transition: "all 0.3s ease"
  }
};

export default JDInput;
