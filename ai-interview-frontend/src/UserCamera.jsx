import React, { useEffect, useRef, useState } from 'react';

const UserCamera = () => {
  const videoRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(false);

  const startCamera = async () => {
    try {
      // Request video and audio permissions
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      
      // Attach the stream to the video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setHasPermission(true);
    } catch (err) {
      console.error("Error accessing camera: ", err);
      alert("Please allow camera access to continue the interview.");
    }
  };

  // Turn on camera as soon as the component loads
  useEffect(() => {
    startCamera();
    
    // Cleanup function to turn off camera when leaving the page
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="camera-container">
      {!hasPermission && <p>Requesting camera access...</p>}
      <video 
        ref={videoRef} 
        autoPlay 
        playsInline 
        muted // Mute so the user doesn't hear their own microphone echo
        style={{ width: '400px', borderRadius: '10px', transform: 'scaleX(-1)' }} 
      />
    </div>
  );
};

export default UserCamera;