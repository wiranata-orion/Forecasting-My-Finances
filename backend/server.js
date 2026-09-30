const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const expensesRouter = require('./routes/expenses');

const app = express();
const port = 5000;

app.use(cors());
app.use(bodyParser.json());

app.use('/api/expenses', expensesRouter);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});