$ErrorActionPreference = 'Stop'

# Run from repo root
if (-not (Test-Path -Path '.git')) {
  Write-Error 'Execute este script na raiz do repo (onde existe .git).'
}

if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
  Write-Error 'Supabase CLI não encontrado no PATH. Instale/abra um novo terminal.'
}

Write-Host 'Cole o token do Supabase (não será exibido):'
$secure = Read-Host -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

if ([string]::IsNullOrWhiteSpace($token)) {
  Write-Error 'Token vazio. Gere um token em https://supabase.com/dashboard/account/tokens'
}

$token = $token.Trim()

if ($token -notmatch '^sbp_[A-Za-z0-9]') {
  Write-Error 'Formato de token inválido. Ele deve começar com sbp_... (cole o token completo, sem aspas).'
}

# Login via token (non-interactive)
& supabase login --token $token
if ($LASTEXITCODE -ne 0) {
  throw "Falha no supabase login (exit=$LASTEXITCODE). Gere um novo token e tente novamente."
}

# Link this workspace to the Supabase project
$projectRef = 'jvovcsuzahfwakcyltfe'
& supabase link --project-ref $projectRef
if ($LASTEXITCODE -ne 0) {
  throw "Falha no supabase link (exit=$LASTEXITCODE)."
}

Write-Host "OK: logado e linkado ao projeto $projectRef"