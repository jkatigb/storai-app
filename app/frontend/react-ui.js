import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, Select, Card, Heading } from './components/ui';
import StoryCreationFlow from './StoryCreationFlow';

const fonts = [
  { name: 'Storybook', value: '"Comic Sans MS", cursive' },
  { name: 'Classic', value: '"Georgia", serif' },
  { name: 'Modern', value: '"Arial", sans-serif' },
  { name: 'Whimsical', value: '"Papyrus", fantasy' },
  { name: 'Typewriter', value: '"Courier New", monospace' },
];

const pageVariants = {
  initial: { opacity: 0, y: 50 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -50 }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.5
};

const App = () => {
  const [view, setView] = useState('creation');
  const [storyData, setStoryData] = useState(null);

  const handleStoryCreated = (data) => {
    setStoryData(data);
    setView('preview');
  };

  return (
    <div className="min-h-screen bg-blue-50 p-8">
      {view === 'creation' && (
        <StoryCreationFlow onStoryCreated={handleStoryCreated} />
      )}
      {view === 'preview' && storyData && (
        <StorybookPage storyData={storyData} />
      )}
    </div>
  );
};

const StorybookPage = ({ storyData }) => {
  const [selectedFont, setSelectedFont] = useState(fonts[0].value);
  const [currentPage, setCurrentPage] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const nextPage = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setCurrentPage((prev) => (prev + 1) % storyData.pages.length);
  };

  useEffect(() => {
    const timer = setTimeout(() => setIsAnimating(false), 500);
    return () => clearTimeout(timer);
  }, [currentPage]);

  return (
    <Card className="relative overflow-hidden rounded-3xl" style={{ width: '1024px', height: '768px' }}>
      <div className="absolute inset-0 bg-gradient-to-b from-blue-50 to-green-50"></div>
      
      <AnimatePresence initial={false} mode="wait">
        <motion.div
          key={currentPage}
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
          className="flex absolute inset-0 p-8"
        >
          {/* Image Section */}
          <div className="w-1/2 p-4 flex items-center justify-center">
            <div className="relative">
              <img src={storyData.pages[currentPage].image} alt={`Storybook Page ${currentPage + 1}`} className="max-w-full max-h-full object-contain rounded-2xl shadow-md" style={{ backgroundColor: '#FFF8E8' }} />
              {/* Decorative elements */}
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-contain bg-no-repeat" style={{ backgroundImage: "url('/api/placeholder/48/48?text=🌟')" }}></div>
              <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-contain bg-no-repeat" style={{ backgroundImage: "url('/api/placeholder/48/48?text=🌈')" }}></div>
            </div>
          </div>

          {/* Text Section */}
          <div className="w-1/2 p-4 flex flex-col">
            <div className="mb-4 flex justify-between items-center">
              <Select
                value={selectedFont}
                onChange={(e) => setSelectedFont(e.target.value)}
                className="w-[180px] bg-yellow-100 border-yellow-200 text-yellow-700"
              >
                {fonts.map((font) => (
                  <option key={font.value} value={font.value}>
                    {font.name}
                  </option>
                ))}
              </Select>
              <Heading level={3} className="text-blue-600" style={{ fontFamily: '"Comic Sans MS", cursive' }}>Page {currentPage + 1}</Heading>
            </div>
            <div 
              className="flex-grow bg-white bg-opacity-80 p-6 rounded-2xl shadow-inner overflow-y-auto border-4 border-yellow-100"
              style={{ fontFamily: selectedFont }}
            >
              <p className="text-xl leading-relaxed text-gray-700">{storyData.pages[currentPage].text}</p>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Next Page Button */}
      <Button 
        className="absolute bottom-8 right-8 bg-green-400 hover:bg-green-500 text-white px-6 py-3 rounded-full shadow-md transform transition hover:scale-105 text-lg font-bold"
        onClick={nextPage}
        disabled={isAnimating}
        style={{ fontFamily: '"Comic Sans MS", cursive' }}
      >
        Next Page
      </Button>
    </Card>
  );
};

export default App;