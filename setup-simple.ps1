# Simple Setup Script for KnowledgeExplorer
# This script helps you configure API keys (emoji-free version)

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " KnowledgeExplorer Setup Wizard  " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$envFile = ".env"

# Check if .env exists
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] .env file created" -ForegroundColor Green
}

Write-Host "Current API Key Status:" -ForegroundColor Yellow
Write-Host ""

$envContent = Get-Content $envFile -Raw

# Check each API key
$groqConfigured = $envContent -match 'GROQ_API_KEY=(?!your_groq_api_key_here)(.+)'
$pineconeConfigured = $envContent -match 'PINECONE_API_KEY=(?!your_pinecone_api_key_here)(.+)'
$jinaConfigured = $envContent -match 'JINA_API_KEY=(?!your_jina_api_key_here)(.+)'

if ($groqConfigured) {
    Write-Host "[OK] Groq API Key: Configured" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Groq API Key: NOT CONFIGURED" -ForegroundColor Red
}

if ($pineconeConfigured) {
    Write-Host "[OK] Pinecone API Key: Configured" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Pinecone API Key: NOT CONFIGURED" -ForegroundColor Red
}

if ($jinaConfigured) {
    Write-Host "[OK] Jina AI Key: Configured" -ForegroundColor Green
} else {
    Write-Host "[OPTIONAL] Jina AI Key: NOT CONFIGURED (will use local embeddings)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Interactive configuration
$configure = Read-Host "Would you like to configure API keys now? (y/n)"

if ($configure -eq "y") {
    Write-Host ""
    Write-Host "API Key Configuration" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host ""
    
    $envLines = Get-Content $envFile
    
    # Groq
    Write-Host "1. Groq API Key (Required)" -ForegroundColor Yellow
    Write-Host "   Get it from: https://console.groq.com/keys" -ForegroundColor Gray
    $newGroqKey = Read-Host "   Enter your Groq API key (or press Enter to skip)"
    if ($newGroqKey) {
        $envLines = $envLines -replace 'GROQ_API_KEY=.+', "GROQ_API_KEY=$newGroqKey"
        Write-Host "   [OK] Groq key updated" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Pinecone
    Write-Host "2. Pinecone API Key (Required)" -ForegroundColor Yellow
    Write-Host "   Get it from: https://app.pinecone.io/" -ForegroundColor Gray
    $newPineconeKey = Read-Host "   Enter your Pinecone API key (or press Enter to skip)"
    if ($newPineconeKey) {
        $envLines = $envLines -replace 'PINECONE_API_KEY=.+', "PINECONE_API_KEY=$newPineconeKey"
        Write-Host "   [OK] Pinecone key updated" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "   Pinecone Environment:" -ForegroundColor Yellow
        $newPineconeEnv = Read-Host "   Enter your Pinecone environment (e.g. us-east-1-aws) or press Enter for default"
        if ($newPineconeEnv) {
            $envLines = $envLines -replace 'PINECONE_ENV=.+', "PINECONE_ENV=$newPineconeEnv"
        }
        
        Write-Host ""
        Write-Host "   Pinecone Index Name:" -ForegroundColor Yellow
        $newPineconeIndex = Read-Host "   Enter your Pinecone index name or press Enter for 'knowledge-explorer'"
        if ($newPineconeIndex) {
            $envLines = $envLines -replace 'PINECONE_INDEX=.+', "PINECONE_INDEX=$newPineconeIndex"
        }
    }
    
    Write-Host ""
    
    # Jina (optional)
    Write-Host "3. Jina AI API Key (Optional)" -ForegroundColor Yellow
    Write-Host "   Get it from: https://jina.ai/" -ForegroundColor Gray
    Write-Host "   Note: If skipped, will use local embeddings (slower but free)" -ForegroundColor Gray
    $newJinaKey = Read-Host "   Enter your Jina API key (or press Enter to skip)"
    if ($newJinaKey) {
        $envLines = $envLines -replace 'JINA_API_KEY=.+', "JINA_API_KEY=$newJinaKey"
        Write-Host "   [OK] Jina key updated" -ForegroundColor Green
    }
    
    # Save .env file
    $envLines | Set-Content $envFile
    Write-Host ""
    Write-Host "[OK] Configuration saved to .env" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure you have created a Pinecone index:" -ForegroundColor Yellow
Write-Host "   - Name: knowledge-explorer (or your custom name)" -ForegroundColor Gray
Write-Host "   - Dimensions: 768" -ForegroundColor Gray
Write-Host "   - Metric: cosine" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the backend:" -ForegroundColor Yellow
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. In a new terminal, start the frontend:" -ForegroundColor Yellow
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Open your browser:" -ForegroundColor Yellow
Write-Host "   http://localhost:8080" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Upload a document and start asking questions!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more help, see:" -ForegroundColor Cyan
Write-Host "   - CURRENT_STATUS.md (start here!)" -ForegroundColor Gray
Write-Host "   - TROUBLESHOOTING.md" -ForegroundColor Gray
Write-Host "   - ISSUE_RESOLVED.md" -ForegroundColor Gray
Write-Host ""
