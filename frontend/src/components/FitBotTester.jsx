import React, { useState } from 'react';
import { Activity, MessageSquare, Mic, Volume2, Video, Heart, Send, Loader2 } from 'lucide-react';

const API_BASE = 'https://fitbot-api-cks6.onrender.com';

export default function FitBotTester() {
  const [activeTab, setActiveTab] = useState('health');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  // Chat state
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  
  // TTS state
  const [ttsText, setTtsText] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  
  // STT state
  const [audioFile, setAudioFile] = useState(null);

  const testHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const testChat = async () => {
    if (!chatMessage.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatMessage,
          user_id: "tester",
          chat_history: []
        })
      });
      const data = await response.json();
      setChatHistory([...chatHistory, { user: chatMessage, bot: data.response || data.error }]);
      setResult(data);
      setChatMessage('');
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const testTTS = async () => {
    if (!ttsText.trim()) return;
    
    setLoading(true);
    setError(null);
    setAudioUrl(null);
    try {
      const response = await fetch(`${API_BASE}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: ttsText,
          voice: "en_US-lessac-medium"
        })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setResult({ success: true, message: 'Audio generated successfully' });
      } else {
        const data = await response.json();
        setError(data.error || 'TTS failed');
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const testSTT = async () => {
    if (!audioFile) return;
    
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', audioFile); // Changed 'audio' to 'file' to match FastAPI endpoint
      
      const response = await fetch(`${API_BASE}/stt`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const testTutorials = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/tutorials`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'health', label: 'Health Check', icon: Heart },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'tts', label: 'Text-to-Speech', icon: Volume2 },
    { id: 'stt', label: 'Speech-to-Text', icon: Mic },
    { id: 'tutorials', label: 'Tutorials', icon: Video }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8" />
              <div>
                <h1 className="text-2xl font-bold">FitBot API Tester</h1>
                <p className="text-blue-100 text-sm">Test all endpoints of your fitness coaching API</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b overflow-x-auto">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setResult(null);
                    setError(null);
                  }}
                  className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Health Check */}
            {activeTab === 'health' && (
              <div className="space-y-4">
                <p className="text-gray-600">Check if the API is running and healthy.</p>
                <button
                  onClick={testHealth}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Heart className="w-4 h-4" />}
                  Test Health Endpoint
                </button>
              </div>
            )}

            {/* Chat */}
            {activeTab === 'chat' && (
              <div className="space-y-4">
                <p className="text-gray-600">Send messages to the AI fitness coach.</p>
                
                {chatHistory.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4 space-y-3 max-h-64 overflow-y-auto">
                    {chatHistory.map((msg, i) => (
                      <div key={i} className="space-y-2">
                        <div className="bg-blue-100 text-blue-900 rounded-lg p-3 ml-8">
                          <p className="text-sm font-medium">You:</p>
                          <p>{msg.user}</p>
                        </div>
                        <div className="bg-white border rounded-lg p-3 mr-8">
                          <p className="text-sm font-medium text-gray-700">FitBot:</p>
                          <p>{msg.bot}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && testChat()}
                    placeholder="Ask about workouts, nutrition, exercises..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={testChat}
                    disabled={loading || !chatMessage.trim()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            )}

            {/* TTS */}
            {activeTab === 'tts' && (
              <div className="space-y-4">
                <p className="text-gray-600">Convert text to speech using Piper.</p>
                <textarea
                  value={ttsText}
                  onChange={(e) => setTtsText(e.target.value)}
                  placeholder="Enter text to convert to speech..."
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 h-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={testTTS}
                  disabled={loading || !ttsText.trim()}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Volume2 className="w-4 h-4" />}
                  Generate Speech
                </button>
                
                {audioUrl && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 font-medium mb-2">Audio Generated!</p>
                    <audio controls src={audioUrl} className="w-full" />
                  </div>
                )}
              </div>
            )}

            {/* STT */}
            {activeTab === 'stt' && (
              <div className="space-y-4">
                <p className="text-gray-600">Convert speech to text using Whisper.</p>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setAudioFile(e.target.files[0])}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {audioFile && (
                  <p className="text-sm text-gray-600">Selected: {audioFile.name}</p>
                )}
                <button
                  onClick={testSTT}
                  disabled={loading || !audioFile}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
                  Transcribe Audio
                </button>
              </div>
            )}

            {/* Tutorials */}
            {activeTab === 'tutorials' && (
              <div className="space-y-4">
                <p className="text-gray-600">Get available exercise tutorial videos.</p>
                <button
                  onClick={testTutorials}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Video className="w-4 h-4" />}
                  Get Tutorials
                </button>
              </div>
            )}

            {/* Results */}
            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">Error:</p>
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {result && activeTab !== 'chat' && (
              <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-gray-700 font-medium mb-2">Response:</p>
                <pre className="bg-white p-3 rounded border text-sm overflow-x-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="mt-4 bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">
            <strong>API Base URL:</strong> {API_BASE}
          </p>
        </div>
      </div>
    </div>
  );
}
