# Execute Ruff formatting and linting
ruff:
	@ruff check --fix .
	@ruff format .


# Run the email automation
automation:
	@docker compose up --build;


# Drop artifacts from development (NOTE: should clean this up
# in the script eventually))
clean:
	@rm -r temp_attachments_* || true
	@rm FERGUSON*.zip || true