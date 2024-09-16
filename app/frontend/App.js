import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import StoryCreationFlow from './StoryCreationFlow';
import StorybookPage from './StorybookPage';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-blue-50">
        <Switch>
          <Route exact path="/" component={StoryCreationFlow} />
          <Route path="/preview" component={StorybookPage} />
        </Switch>
      </div>
    </Router>
  );
};

export default App;