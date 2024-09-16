import React, { useState, useEffect } from 'react';
import { Button, Input, TextArea, Select, Spinner, Card, Heading } from './components/ui';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const StoryCreationFlow = ({ onStoryCreated }) => {
  const [step, setStep] = useState('input');
  const [storyParams, setStoryParams] = useState({
    age_range: '',
    themes: [],
    moral: '',
    characters: [],
    story_setting: '',
    tone: '',
  });
  const [synopsis, setSynopsis] = useState('');
  const [outline, setOutline] = useState(null);
  const [enhancedOutline, setEnhancedOutline] = useState(null);
  const [currentSection, setCurrentSection] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [taskId, setTaskId] = useState(null);

  const handleInputChange = (e) => {
    setStoryParams({ ...storyParams, [e.target.name]: e.target.value });
  };

  const handleArrayInputChange = (e) => {
    setStoryParams({ ...storyParams, [e.target.name]: e.target.value.split(',') });
  };

  const handleCharacterChange = (index, field, value) => {
    const updatedCharacters = [...storyParams.characters];
    updatedCharacters[index][field] = value;
    setStoryParams({ ...storyParams, characters: updatedCharacters });
  };

  const addCharacter = () => {
    setStoryParams({
      ...storyParams,
      characters: [...storyParams.characters, { name: '', description: '' }],
    });
  };

  const pollTaskStatus = async (taskId) => {
    try {
      const response = await axios.get(`${API_URL}/api/story/task/${taskId}`);
      if (response.data.status === 'completed') {
        // Fetch the result based on the task type
        await fetchTaskResult(taskId);
      } else if (response.data.status === 'failed') {
        setError('Task processing failed. Please try again.');
        setLoading(false);
      } else {
        // If the task is still processing, poll again after a delay
        setTimeout(() => pollTaskStatus(taskId), 2000);
      }
    } catch (err) {
      setError('Failed to check task status. Please try again.');
      setLoading(false);
    }
  };

  const fetchTaskResult = async (taskId) => {
    try {
      const response = await axios.get(`${API_URL}/api/story/task/${taskId}/result`);
      const result = response.data.result;
      
      switch (response.data.task_type) {
        case 'synopsis':
          setSynopsis(result);
          setStep('synopsis');
          break;
        case 'outline':
          setOutline(result);
          setStep('outline');
          break;
        case 'enhance_outline':
          setEnhancedOutline(result);
          setStep('enhanced_outline');
          break;
        case 'develop_section':
          setCurrentSection({ name: result.section_name, content: result.content });
          setStep('section_development');
          break;
        default:
          setError('Unknown task type');
      }
    } catch (err) {
      setError('Failed to fetch task result. Please try again.');
    }
    setLoading(false);
  };

  const generateSynopsis = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/story/synopsis`, { parameters: storyParams });
      setTaskId(response.data.task_id);
      pollTaskStatus(response.data.task_id);
    } catch (err) {
      setError('Failed to generate synopsis. Please try again.');
      setLoading(false);
    }
  };

  const generateOutline = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/story/outline`, { parameters: storyParams });
      setTaskId(response.data.task_id);
      pollTaskStatus(response.data.task_id);
    } catch (err) {
      setError('Failed to generate outline. Please try again.');
      setLoading(false);
    }
  };

  const enhanceOutline = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/story/enhance-outline`, { outline });
      setTaskId(response.data.task_id);
      pollTaskStatus(response.data.task_id);
    } catch (err) {
      setError('Failed to enhance outline. Please try again.');
      setLoading(false);
    }
  };

  const developSection = async (sectionName) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/story/develop-section`, {
        section_name: sectionName,
        section_outline: enhancedOutline.plot[sectionName],
        additional_context: enhancedOutline,
      });
      setTaskId(response.data.task_id);
      pollTaskStatus(response.data.task_id);
    } catch (err) {
      setError(`Failed to develop section ${sectionName}. Please try again.`);
      setLoading(false);
    }
  };

  const renderStoryInput = () => (
    <Card>
      <Heading level={2}>Create Your Story</Heading>
      <div className="space-y-4">
        <Input
          name="age_range"
          placeholder="Age Range (e.g., 3-5)"
          value={storyParams.age_range}
          onChange={handleInputChange}
        />
        <Input
          name="themes"
          placeholder="Themes (comma-separated)"
          value={storyParams.themes.join(',')}
          onChange={handleArrayInputChange}
        />
        <Input
          name="moral"
          placeholder="Moral of the story"
          value={storyParams.moral}
          onChange={handleInputChange}
        />
        <Input
          name="story_setting"
          placeholder="Story Setting"
          value={storyParams.story_setting}
          onChange={handleInputChange}
        />
        <Input
          name="tone"
          placeholder="Tone of the story"
          value={storyParams.tone}
          onChange={handleInputChange}
        />
        <Heading level={3}>Characters</Heading>
        {storyParams.characters.map((char, index) => (
          <div key={index} className="space-y-2">
            <Input
              placeholder="Character Name"
              value={char.name}
              onChange={(e) => handleCharacterChange(index, 'name', e.target.value)}
            />
            <Input
              placeholder="Character Description"
              value={char.description}
              onChange={(e) => handleCharacterChange(index, 'description', e.target.value)}
            />
          </div>
        ))}
        <Button onClick={addCharacter} className="bg-green-500 hover:bg-green-600">Add Character</Button>
        <Button onClick={generateSynopsis} className="bg-blue-500 hover:bg-blue-600">Generate Synopsis</Button>
      </div>
    </Card>
  );

  const renderSynopsis = () => (
    <Card>
      <Heading level={2}>Story Synopsis</Heading>
      <p className="mb-4">{synopsis}</p>
      <div className="space-x-4">
        <Button onClick={() => setStep('input')} className="bg-gray-500 hover:bg-gray-600">Edit Parameters</Button>
        <Button onClick={generateOutline} className="bg-blue-500 hover:bg-blue-600">Generate Outline</Button>
      </div>
    </Card>
  );

  const renderOutline = () => (
    <Card>
      <Heading level={2}>Story Outline</Heading>
      <pre className="bg-gray-100 p-4 rounded-md overflow-auto mb-4">{JSON.stringify(outline, null, 2)}</pre>
      <Button onClick={enhanceOutline} className="bg-blue-500 hover:bg-blue-600">Enhance Outline</Button>
    </Card>
  );

  const renderEnhancedOutline = () => (
    <Card>
      <Heading level={2}>Enhanced Story Outline</Heading>
      <pre className="bg-gray-100 p-4 rounded-md overflow-auto mb-4">{JSON.stringify(enhancedOutline, null, 2)}</pre>
      <Heading level={3}>Develop Sections</Heading>
      <div className="grid grid-cols-2 gap-4">
        {Object.keys(enhancedOutline.plot).map((sectionName) => (
          <Button key={sectionName} onClick={() => developSection(sectionName)} className="bg-green-500 hover:bg-green-600">
            Develop {sectionName}
          </Button>
        ))}
      </div>
    </Card>
  );

  const renderSectionDevelopment = () => (
    <Card>
      <Heading level={2}>Developed Section: {currentSection.name}</Heading>
      <p className="mb-4">{currentSection.content}</p>
      <Button onClick={() => setStep('enhanced_outline')} className="bg-blue-500 hover:bg-blue-600">Back to Outline</Button>
    </Card>
  );

  return (
    <div className="max-w-4xl mx-auto p-4">
      {loading && <Spinner />}
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {taskId && <p className="text-blue-500 mb-4">Task ID: {taskId}</p>}
      {step === 'input' && renderStoryInput()}
      {step === 'synopsis' && renderSynopsis()}
      {step === 'outline' && renderOutline()}
      {step === 'enhanced_outline' && renderEnhancedOutline()}
      {step === 'section_development' && renderSectionDevelopment()}
    </div>
  );
};

export default StoryCreationFlow;