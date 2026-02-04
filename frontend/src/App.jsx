import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, CheckCircle, XCircle, AlertTriangle, Play, Settings, FileText } from 'lucide-react'

function App() {
  const [prompt, setPrompt] = useState('')
  const [output, setOutput] = useState('')
  const [config, setConfig] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const runValidation = async () => {
    setLoading(true)
    // Simulate API call
    await new Promise(r => setTimeout(r, 1500))
    
    setResult({
      score: 82.5,
      passed: true,
      assertions: [
        { name: 'max_length', passed: true, message: 'Within limits (150 tokens)', score: 1.0 },
        { name: 'no_secrets', passed: true, message: 'No prohibited patterns', score: 1.0 },
        { name: 'has_steps', passed: true, message: 'Contains "step" (3 times)', score: 1.0 },
        { name: 'professional', passed: false, message: 'Found: "yeah" (informal)', score: 0.5 }
      ]
    })
    setLoading(false)
  }

  return (
    <div className="min-h-screen p-8" style={{ background: 'linear-gradient(-45deg, #0a0a0f, #1a1a2e, #16213e)' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Shield className="w-10 h-10 text-claw-500" />
            LLM Validator
          </h1>
          <p className="text-gray-400">Test and validate AI outputs against assertions</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card rounded-2xl p-6"
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-claw-400" />
              Input
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Prompt</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full h-24 bg-white/5 border border-white/10 rounded-lg p-3 text-white"
                  placeholder="Enter your prompt..."
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">LLM Output</label>
                <textarea
                  value={output}
                  onChange={(e) => setOutput(e.target.value)}
                  className="w-full h-40 bg-white/5 border border-white/10 rounded-lg p-3 text-white"
                  placeholder="Paste LLM output to validate..."
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Validation Config (JSON)</label>
                <textarea
                  value={config}
                  onChange={(e) => setConfig(e.target.value)}
                  className="w-full h-32 bg-white/5 border border-white/10 rounded-lg p-3 text-white font-mono text-sm"
                  placeholder='{"name":"test","assertions":[...]}'
                />
              </div>
              
              <button
                onClick={runValidation}
                disabled={loading}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-claw-600 to-purple-600 font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <span className="animate-pulse">Running...</span>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Run Validation
                  </>
                )}
              </button>
            </div>
          </motion.div>

          {/* Results Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card rounded-2xl p-6"
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-claw-400" />
              Results
            </h2>
            
            {!result ? (
              <div className="text-center text-gray-500 py-12">
                <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Run a validation to see results</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Score */}
                <div className="text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${
                      result.passed ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}
                  >
                    <span className={`text-4xl font-bold ${result.passed ? 'text-green-400' : 'text-red-400'}`}>
                      {result.score}
                    </span>
                  </motion.div>
                  <p className="mt-2 font-medium">
                    {result.passed ? '✅ PASSED' : '❌ FAILED'}
                  </p>
                </div>
                
                {/* Assertions */}
                <div className="space-y-2">
                  <h3 className="text-sm text-gray-400">Assertions</h3>
                  {result.assertions.map((assertion, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                    >
                      <span className="flex items-center gap-2">
                        {assertion.passed ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                        {assertion.name}
                      </span>
                      <span className="text-sm text-gray-400">{assertion.message}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default App
