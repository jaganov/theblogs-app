-- Installing necessary PostgreSQL extensions
\c theblogs;

-- Check installed extensions
SELECT extname, extversion FROM pg_extension ORDER BY extname;