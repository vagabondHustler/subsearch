$svg = "subsearch.svg"
$sizes = @(16, 24, 32, 48, 64, 128, 256, 512)

Write-Host "Exporting PNGs..."

foreach ($size in $sizes) {
  $png = "$size.png"

  inkscape `
    $svg `
    --export-type=png `
    --export-width=$size `
    --export-height=$size `
    --export-filename=$png

  if ($LASTEXITCODE -eq 0) {
    Write-Host "Created $png"
  }
  else {
    Write-Host "Failed to create $png"
    exit 1
  }
}

Write-Host ""
Write-Host "Creating subsearch.ico..."

magick ($sizes | ForEach-Object { "$_.png" }) subsearch.ico

if ($LASTEXITCODE -ne 0) {
  Write-Host "Failed to create subsearch.ico"
  exit 1
}

Write-Host "Created subsearch.ico"

Write-Host ""
Write-Host "Cleaning up..."

foreach ($size in $sizes) {
  $png = "$size.png"
  Remove-Item $png
  Write-Host "Deleted $png"
}

Write-Host ""
Write-Host "Done."