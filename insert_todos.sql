-- Insert 5 todo items into the todo_items table
INSERT INTO todo_items (title, description, priority, completed) VALUES
('Complete FastAPI tutorial', 'Finish learning FastAPI basics and build a todo app', 1, false),
('Buy groceries', 'Get milk, bread, eggs, and vegetables from the store', 2, false),
('Exercise routine', 'Go for a 30-minute run in the park', 1, false),
('Read a book', 'Read at least one chapter of "Clean Code"', 3, false),
('Prepare presentation', 'Create slides for the team meeting next week', 1, true);

-- Check the inserted data
SELECT * FROM todo_items;
