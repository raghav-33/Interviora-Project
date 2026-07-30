import { useState, useEffect, useRef } from "react";
import UserCamera from "./UserCamera";

function Interview({ sessionId, questions }) {
  const [index, setIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(questions[0]);
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");

  const [feedback, setFeedback] = useState(null);
  const [interviewDone, setInterviewDone] = useState(false);
  const [loadingNext, setLoadingNext] = useState(false);

  const recognitionRef = useRef(null);

  // 🔊 Speak Question
  const speakQuestion = (text) => {
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    if (currentQuestion) {
      speakQuestion(currentQuestion);
    }
  }, [currentQuestion]);

  // 🎤 Setup Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let text = "";
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript;
      }
      setTranscript(text);
    };

    recognitionRef.current = recognition;
  }, []);

  // ▶️ Start Recording
  const startRecording = () => {
    setTranscript("");
    recognitionRef.current.start();
    setRecording(true);
  };

  // ⏹ Stop Recording & Submit Answer
  const stopRecording = async () => {
    recognitionRef.current.stop();
    setRecording(false);

    if (!transcript.trim()) {
      alert("Please speak something before stopping.");
      return;
    }

    try {
      setLoadingNext(true);
      console.log(`[Frontend] Submitting answer for session: ${sessionId}`);

      await fetch("http://127.0.0.1:8000/submit-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          answer: transcript
        })
      });

      console.log("[Frontend] Answer submitted successfully. Loading next question...");
      await loadNextQuestion();

    } catch (error) {
      console.error("[Frontend] Error submitting answer:", error);
    } finally {
      setLoadingNext(false);
    }
  };

  // 👉 Load Next Question
  const loadNextQuestion = async () => {
    console.log(`[Frontend] Requesting next question. Next index should be: ${index + 1}`);
    
    try {
      const res = await fetch("http://127.0.0.1:8000/next-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          index: index + 1
        })
      });

      const data = await res.json();
      console.log("[Frontend] Backend responded to next-question with:", data);

      if (data.done) {
        console.log("[Frontend] Backend says interview is done! Triggering feedback phase...");
        setInterviewDone(true);
        await generateFeedback(); 
        return;
      }

      setIndex(data.index);
      setCurrentQuestion(data.question);
      setTranscript("");
    } catch (error) {
      console.error("[Frontend] Error loading next question:", error);
    }
  };

  // 🔥 Generate Feedback
  const generateFeedback = async () => {
    console.log(`[Frontend] Preparing to send feedback request for session: ${sessionId}`);
    
    try {
      const res = await fetch("http://127.0.0.1:8000/generate-feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
      });

      console.log("[Frontend] Feedback request sent. Waiting for AI...");

      if (!res.ok) {
        throw new Error(`Server responded with status: ${res.status}`);
      }

      const data = await res.json();
      console.log("[Frontend] Feedback received successfully!", data);
      setFeedback(data.feedback);
      
    } catch (error) {
      console.error("[Frontend] CRITICAL ERROR fetching feedback:", error);
      alert("The frontend failed to fetch the feedback. Check the browser console (F12).");
      setInterviewDone(false); // Remove loading screen so user isn't stuck
    }
  };

  // ⏳ LOADING SCREEN
  if (interviewDone && !feedback) {
    return (
      <div style={styles.container}>
        <h2>🔄 Generating your AI feedback...</h2>
        <p style={{ color: "#94a3b8", marginTop: "10px" }}>
          Our AI Manager is evaluating your responses. This will take a few seconds.
        </p>
      </div>
    );
  }

  // 🎉 FEEDBACK SCREEN
  if (interviewDone && feedback) {
    return (
      <div style={styles.container}>
        <h2>🎉 Interview Completed</h2>

        <div style={styles.card}>
          <h3>Score: {feedback.score}/100</h3>

          <h4>✅ Strengths</h4>
          <ul>
            {feedback.strengths.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>

          <h4>⚡ Improvements</h4>
          <ul>
            {feedback.improvements.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>

          <h4>🏁 Verdict: {feedback.verdict}</h4>
        </div>
      </div>
    );
  }

  // 🎤 INTERVIEW SCREEN
  return (
    <div style={styles.container}>
      <UserCamera />
      
      <h2>Question {index + 1} / {questions.length}</h2>

      <div style={styles.questionBox}>
        {currentQuestion}
      </div>

      {transcript && (
        <div style={styles.transcriptBox}>
          <strong>📝 Live Answer:</strong>
          <p>{transcript}</p>
        </div>
      )}

      {!recording ? (
        <button style={styles.button} onClick={startRecording}>
          🎤 Start Answer
        </button>
      ) : (
        <button
          style={{ ...styles.button, backgroundColor: "#ef4444" }}
          onClick={stopRecording}
        >
          ⏹ Stop Answer
        </button>
      )}

      {loadingNext && <p style={{ marginTop: "15px" }}>Processing...</p>}
    </div>
  );
}

const styles = {
  container: {
    width: "700px",
    background: "#1e293b",
    padding: "40px",
    borderRadius: "20px",
    boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
  },
  questionBox: {
    marginTop: "20px",
    padding: "20px",
    background: "#0f172a",
    borderRadius: "12px",
    fontSize: "16px",
    lineHeight: "1.6",
  },
  transcriptBox: {
    marginTop: "20px",
    padding: "15px",
    background: "#0f172a",
    borderRadius: "12px",
    color: "#94a3b8",
  },
  card: {
    background: "#0f172a",
    padding: "30px",
    borderRadius: "16px",
    marginTop: "20px",
    textAlign: "left",
  },
  button: {
    marginTop: "25px",
    padding: "14px",
    width: "100%",
    borderRadius: "12px",
    border: "none",
    fontSize: "16px",
    background: "linear-gradient(90deg, #6366f1, #4f46e5)",
    color: "white",
    cursor: "pointer",
  }
};

export default Interview;