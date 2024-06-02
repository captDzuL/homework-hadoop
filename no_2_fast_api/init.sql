CREATE TABLE pokemon_effect (
   id SERIAL PRIMARY KEY,
   loan_id INTEGER,
   user_id INTEGER,
   pokemon_ability_id INTEGER,
   effect TEXT,
   language TEXT,
   short_effect TEXT
);
