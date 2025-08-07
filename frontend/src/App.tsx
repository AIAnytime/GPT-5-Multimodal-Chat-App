import React, { useState, useRef } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { 
  Send, 
  Copy, 
  Upload, 
  MessageSquare,
  Sparkles,
  FileText,
  Eye,
  Search,
  RotateCcw,
  Bot,
  User
} from 'lucide-react';
import './App.css';
import './markdown.css';
import 'highlight.js/styles/github-dark.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  response: string;
  conversation_history: Message[];
  analysis_type?: string;
}

const API_BASE_URL = 'http://localhost:8000';

// Default questions to show users
const DEFAULT_QUESTIONS = [
  "What is artificial intelligence?",
  "Explain machine learning in simple terms",
  "How does neural networks work?",
  "What are the applications of AI?"
];

// Preset actions for image analysis
const PRESET_ACTIONS = [
  { key: 'analyze', label: 'Analyze', icon: Search, description: 'Detailed analysis' },
  { key: 'summarize', label: 'Summarize', icon: FileText, description: 'Quick summary' },
  { key: 'describe', label: 'Describe', icon: Eye, description: 'Detailed description' },
  { key: 'extract_text', label: 'Extract Text', icon: FileText, description: 'OCR text extraction' }
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [showPresets, setShowPresets] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle file drop
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('image/')) {
      setUploadedImage(file);
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result as string);
        setShowPresets(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    multiple: false
  });

  // Send text message
  const sendTextMessage = async (message: string) => {
    if (!message.trim()) return;

    const newUserMessage: Message = { role: 'user', content: message };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat/text`, {
        message: message,
        conversation_history: messages
      });

      setMessages(response.data.conversation_history);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...updatedMessages, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Send image with preset action
  const sendImageWithPreset = async (presetAction: string) => {
    if (!uploadedImage) return;

    setIsLoading(true);
    setShowPresets(false);

    const formData = new FormData();
    formData.append('image', uploadedImage);
    formData.append('preset_action', presetAction);

    try {
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat/image-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const userMessage: Message = {
        role: 'user',
        content: `[Image uploaded] - ${PRESET_ACTIONS.find(p => p.key === presetAction)?.label}`
      };
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };

      setMessages([...messages, userMessage, assistantMessage]);
    } catch (error) {
      console.error('Error analyzing image:', error);
      setMessages([...messages, {
        role: 'assistant',
        content: 'Sorry, there was an error analyzing the image. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Send image with custom prompt
  const sendImageWithPrompt = async (prompt: string) => {
    if (!uploadedImage || !prompt.trim()) return;

    setIsLoading(true);
    setShowPresets(false);

    const formData = new FormData();
    formData.append('image', uploadedImage);
    formData.append('prompt', prompt);

    try {
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat/image-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const userMessage: Message = {
        role: 'user',
        content: `[Image uploaded] ${prompt}`
      };
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };

      setMessages([...messages, userMessage, assistantMessage]);
      setInputMessage('');
    } catch (error) {
      console.error('Error analyzing image:', error);
      setMessages([...messages, {
        role: 'assistant',
        content: 'Sorry, there was an error analyzing the image. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  // Clear uploaded image
  const clearImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    setShowPresets(false);
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (uploadedImage && inputMessage.trim()) {
      sendImageWithPrompt(inputMessage);
    } else if (inputMessage.trim()) {
      sendTextMessage(inputMessage);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Sparkles className="logo-icon" />
            <h1>GPT-5 Multimodal Chat</h1>
          </div>
          <p className="subtitle">Chat with AI using text and images</p>
        </div>
      </header>

      <main className="app-main">
        {/* Chat Messages */}
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-content">
                <Sparkles className="welcome-icon" />
                <h2>Welcome to GPT-5 Multimodal Chat</h2>
                <p>Ask questions, upload images, or try one of these examples:</p>
                
                <div className="default-questions">
                  {DEFAULT_QUESTIONS.map((question, index) => (
                    <button
                      key={index}
                      className="question-button"
                      onClick={() => sendTextMessage(question)}
                      disabled={isLoading}
                    >
                      <MessageSquare className="question-icon" />
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  <div className="message-avatar">
                    {message.role === 'user' ? (
                      <User className="avatar-icon" />
                    ) : (
                      <Bot className="avatar-icon" />
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      {message.role === 'assistant' ? (
                        <div className="markdown-content">
                          <ReactMarkdown
                            rehypePlugins={[rehypeHighlight]}
                            components={{
                              code: ({ className, children, ...props }: any) => {
                              const match = /language-(\w+)/.exec(className || '');
                              return match ? (
                                <pre className="code-block">
                                  <code className={className} {...props}>
                                    {children}
                                  </code>
                                </pre>
                              ) : (
                                <code className="inline-code" {...props}>
                                  {children}
                                </code>
                              );
                            },
                          }}
                        >
                          {message.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        message.content
                      )}
                    </div>
                    {message.role === 'assistant' && (
                      <button
                        className="copy-button"
                        onClick={() => copyToClipboard(message.content)}
                        title="Copy to clipboard"
                      >
                        <Copy className="copy-icon" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar">
                    <Bot className="avatar-icon" />
                  </div>
                  <div className="message-content">
                    <div className="loading">
                      <div className="loading-dots">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                      </div>
                      <span>AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Image Upload Area */}
        {imagePreview && (
          <div className="image-preview-container">
            <div className="image-preview">
              <img src={imagePreview} alt="Uploaded" className="preview-image" />
              <button className="remove-image" onClick={clearImage}>
                <RotateCcw className="remove-icon" />
              </button>
            </div>
            
            {showPresets && (
              <div className="preset-actions">
                <h3>Quick Actions:</h3>
                <div className="preset-buttons">
                  {PRESET_ACTIONS.map((preset) => {
                    const IconComponent = preset.icon;
                    return (
                      <button
                        key={preset.key}
                        className="preset-button"
                        onClick={() => sendImageWithPreset(preset.key)}
                        disabled={isLoading}
                      >
                        <IconComponent className="preset-icon" />
                        <span>{preset.label}</span>
                      </button>
                    );
                  })}
                </div>
                <p className="preset-hint">Or type a custom question below</p>
              </div>
            )}
          </div>
        )}

        {/* Input Area */}
        <div className="input-container">
          {/* File Upload */}
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <Upload className="upload-icon" />
            <span>{isDragActive ? 'Drop image here' : 'Drag & drop image'}</span>
          </div>

          {/* Text Input */}
          <form onSubmit={handleSubmit} className="input-form">
            <div className="input-wrapper">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={uploadedImage ? "Ask something about the image..." : "Type your message..."}
                className="message-input"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="send-button"
                disabled={isLoading || (!inputMessage.trim() && !uploadedImage)}
              >
                <Send className="send-icon" />
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
