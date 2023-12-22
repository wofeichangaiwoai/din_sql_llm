### Route
```markdown
You are currently doing a classification task. Given a raw text input to a language model select the class best suited for the input. You will be given the names of the available class and a description of what the prompt is best suited for.

<< FORMATTING >>
Return the class name directly, the output should only include one word.

REMEMBER: "class" MUST be one of the candidate names specified below OR it can be "other" if the input is not well suited for any of the candidate prompts.


<< CLASS DEFINITION >>
query: The request to query the table in DB, only for table. Here are some key words: maximum, min, max, avg, table and so on.
other: general questions.
api: The request to create something, or query information about workspace, function, modelspace or action.


<< EXAMPLE >>
class: query, definition: How many records in the table?
class: query, definition: What's the maximum number in table
class: query, definition: Could you help to summary how many sells in this quarter.
class: other, definition: who are you?
class: other, definition: what is your name?
class: other, definition: What is black body radiation?
class: api, definition: help to create a modelspace
class: api, definition: How many workspaces are created

<< INPUT >>
What is the maximum total in this table?

<< OUTPUT (the output should only include one word.) >>
```

### Generate SQL
``` markdown
Given an input question, first create a syntactically correct trino query to run, then look at the results of the query and return the answer. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most 5 results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use the following tables:
CREATE TABLE sales_order_item (total,)

Question: What is the maximum total in this table?
SQLQuery:
```


### Generate the final answer base on the SQL result
```markdown
Given an input question, first create a syntactically correct trino query to run, then look at the results of the query and return the answer. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most 5 results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use the following tables:
CREATE TABLE sales_order_item (total,)

Question: What is the maximum total in this table?
SQLQuery:SELECT MAX(total) FROM sales_order_item
SQLResult: [(Decimal('10000000000.000000'),)]
Answer:

```