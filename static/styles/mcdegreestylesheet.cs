.main-nav {
    display: flex; 
}

.push {
    margin-left: auto; 
}

.flex {
    display: flex; 
    flex-wrap: wrap;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, 50px);
    grid-gap: 10 px;
}

.gridItem {
    grid-column: 1 / -1; 
}

.content {
    max-width: 500px; 
    margin: auto; 

}

.content-wrapper {
    display: block; 
    margin: 10px;
    margin-right: auto; 
    margin-left: auto; 
    
    
    max-width: 90%; 
    background-color: #e6a9a9; 
    text-align: center;
    align-items: center;
    align-content: center;
    color: white;
    border: 1px solid red; 
    box-shadow: 5px 5px 5px grey;

}
div > div {
    box-sizing: border-box;
    border: 2px solid #8c8c8c;
    width:fit-content;
    justify-content:center;
    align-content: center;
    display:block;
    
    
  }

  #container {
    height:200px;
    width: 240px;
    align-items: center; /* Can be changed in the live sample */
    background-color: #8c8c8c;
  }
  
  .flex {
    display: flex;
    flex-wrap: wrap;
  }
  
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, 50px);
  }
  

  
  #item1 {
    background-color: #8cffa0;
    min-height: 30px;
  }
  
  #item2 {
    background-color: #a0c8ff;
    min-height: 50px;
  }
  
  #item3 {
    background-color: #ffa08c;
    min-height: 40px;
  }
  
  #item4 {
    background-color: #ffff8c;
    min-height: 60px;
  }
  
  #item5 {
    background-color: #ff8cff;
    min-height: 70px;
  }
  
  #item6 {
    background-color: #8cffff;
    min-height: 50px;
    font-size: 30px;
  }
  
  select {
    font-size: 16px;
  }
  
  .row {
    align-content: center;
    margin-top: 30px;
    margin-left: 10px;
    border-style: none;
  }

  .title{
    font-size: 50;
    font-family: 'Garamond';
    align-items: center;
  }

  .button {
    background-color:#ffffff;
    border: 2px solid #ff7575;
    color: #ff7575;
    padding: 3px 5px;
    border-radius: 5px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
    font-family: 'Garamond';
  }
  .button:hover {
    background-color:#ff7575;
    color: #ffffff; 
    border: 2px solid #ff7575;
  }

  body {
    background-color: #ffdbdb;
  }