import React, { useState, useEffect } from 'react';
import ReactJson from 'react-json-view';
import { compilePrompt } from './api/client';

const STAGES = [
  { id: 1, name: 'Intent Extraction', key: 'intent_extraction' },
  { id: 2, name: 'Architecture Design', key: 'architecture_design' },
  { id: 3, name: 'Schema Generation', key: 'schema_generation' },
  { id: 4, name: 'Refinement', key: 'refinement' }
];

function App() {
  const [prompt, setPrompt] = useState('');
  const [isCompiling, setIsCompiling] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [results, setResults] = useState({
    1: null,
    2: null,
    3: null,
    4: null
  });
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(1);

  const handleCompile = async () => {
    setIsCompiling(true);
    setError(null);
    setCurrentStage(0);
    setResults({ 1: null, 2: null, 3: null, 4: null });
    setActiveTab(1);

    try {
      await compilePrompt(prompt, (data) => {
        if (data.stage === 'start') {
          setCurrentStage(0);
        } else if (typeof data.stage === 'number') {
          setCurrentStage(data.stage);
          setResults(prev => ({ ...prev, [data.stage]: data.result }));
          setActiveTab(data.stage);
        } else if (data.stage === 'done') {
          setIsCompiling(false);
        } else if (data.stage === 'error') {
          setError(data.message);
          setIsCompiling(false);
        }
      });
    } catch (e) {
      setError(e.message);
      setIsCompiling(false);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-[#7c3aed] mb-2">AppCompiler</h1>
        <p className="text-gray-400">Natural Language → Validated App Schema Pipeline</p>
      </header>

      <div className="grid grid-cols-1 gap-8">
        {/* Prompt Input */}
        <section className="bg-[#1a1a1a] p-6 rounded-xl border border-gray-800 shadow-2xl">
          <textarea
            className="w-full h-32 bg-[#0d0d0d] text-white p-4 rounded-lg border border-gray-700 focus:border-[#7c3aed] focus:ring-1 focus:ring-[#7c3aed] outline-none transition-all resize-none mb-4"
            placeholder="Build a CRM with login, contacts list, and dashboard..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isCompiling}
          />
          <button
            className={`w-full py-3 rounded-lg font-bold text-white transition-all ${
              isCompiling ? 'bg-gray-700 cursor-not-allowed' : 'bg-[#7c3aed] hover:bg-[#6d28d9]'
            }`}
            onClick={handleCompile}
            disabled={isCompiling || !prompt.trim()}
          >
            {isCompiling ? 'Compiling Application...' : 'Compile App Specification'}
          </button>
        </section>

        {/* Pipeline Visualizer */}
        <section className="grid grid-cols-4 gap-4">
          {STAGES.map((stage) => (
            <div
              key={stage.id}
              className={`p-4 rounded-lg border transition-all ${
                currentStage === stage.id
                  ? 'bg-[#7c3aed22] border-[#7c3aed] shadow-[0_0_15px_rgba(124,58,237,0.3)]'
                  : currentStage > stage.id
                  ? 'bg-[#10b98122] border-[#10b981]'
                  : 'bg-[#1a1a1a] border-gray-800'
              }`}
            >
              <div className="text-xs font-mono text-gray-500 mb-1">STAGE {stage.id}</div>
              <div className="font-bold">{stage.name}</div>
              {currentStage === stage.id && (
                <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-[#7c3aed] animate-[progress_2s_ease-in-out_infinite]" style={{ width: '50%' }}></div>
                </div>
              )}
            </div>
          ))}
        </section>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 text-red-200 p-4 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results Viewer */}
        <section className="bg-[#1a1a1a] rounded-xl border border-gray-800 overflow-hidden shadow-2xl">
          <div className="flex border-b border-gray-800">
            {STAGES.map((stage) => (
              <button
                key={stage.id}
                className={`px-6 py-3 font-medium transition-all ${
                  activeTab === stage.id
                    ? 'text-[#7c3aed] border-b-2 border-[#7c3aed] bg-[#7c3aed0a]'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
                onClick={() => setActiveTab(stage.id)}
                disabled={!results[stage.id]}
              >
                {stage.name}
              </button>
            ))}
          </div>
          <div className="p-6 bg-[#0d0d0d] min-h-[400px]">
            {results[activeTab] ? (
              <ReactJson
                src={results[activeTab]}
                theme="monokai"
                displayDataTypes={false}
                enableClipboard={true}
                style={{ backgroundColor: 'transparent' }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-600 italic">
                {isCompiling ? 'Waiting for stage to complete...' : 'No output available yet'}
              </div>
            )}
          </div>
        </section>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}} />
    </div>
  );
}

export default App;
