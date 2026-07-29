@echo off
echo Setting up Git hooks for automatic migrations...
git config core.hooksPath .githooks
echo Git hooks configured successfully!

echo.
echo Running initial database migrations...
python manage.py migrate

echo.
echo Setup complete! You are ready to start development.
pause
