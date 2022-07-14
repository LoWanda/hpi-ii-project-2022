import './App.css';
import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import 'bootstrap/dist/css/bootstrap.min.css';
import Visualization from './Visualization.js'

function App() {
  return (
    <div className="App">
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand>
          Event Visualization
          </Navbar.Brand>
        </Container>
      </Navbar>
      <Visualization />
    </div>
  );
}

export default App;
