# PowerShell script to process documentation files for Mintlify

$ErrorActionPreference = "Stop"

function Get-TitleFromFilename {
    param([string]$filename)
    $name = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    $name = $name -replace '-', ' '
    $name = $name -replace '_', ' '
    # Title case
    $words = $name -split ' '
    $titled = $words | ForEach-Object { $_.Substring(0,1).ToUpper() + $_.Substring(1).ToLower() }
    return $titled -join ' '
}

function Process-DocFile {
    param(
        [string]$filePath,
        [string]$category
    )
    
    $content = Get-Content $filePath -Raw -Encoding UTF8
    $filename = Split-Path $filePath -Leaf
    
    # Skip if already has frontmatter
    if ($content -match "^---") {
        Write-Host "  Skipping (has frontmatter): $filename"
        return
    }
    
    # Extract title from first H1 or generate from filename
    $title = ""
    if ($content -match "^#\s+(.+)") {
        $title = $matches[1] -replace '\(v[\d.]+\)', '' # Remove version
        $title = $title.Trim()
    } else {
        $title = Get-TitleFromFilename $filename
    }
    
    # Generate description
    $description = "Documentation for $title"
    if ($category -eq "cli") {
        $description = "CLI reference for the $title command"
    } elseif ($category -eq "api") {
        $description = "Python API reference for $title"
    } elseif ($category -eq "features") {
        $description = "Feature documentation: $title"
    } elseif ($category -eq "tutorials") {
        $description = "Tutorial: $title"
    }
    
    # Create frontmatter
    $frontmatter = @"
---
title: "$title"
description: "$description"
---

"@
    
    # Remove first H1 heading (will be replaced by frontmatter title)
    $content = $content -replace "^#\s+.+\r?\n\r?\n", ""
    
    # Escape MDX: < followed by alphanumeric (except valid HTML tags)
    $content = $content -replace '<(\d)', '&lt;$1'
    
    # Fix internal links: remove .md extension
    $content = $content -replace '\]\(([^)]+)\.md\)', ']($1)'
    
    # Combine
    $newContent = $frontmatter + $content
    
    # Write back
    Set-Content -Path $filePath -Value $newContent -Encoding UTF8 -NoNewline
    Write-Host "  Processed: $filename"
}

# Process CLI files
Write-Host "`nProcessing CLI files..."
Get-ChildItem "docs/reference/cli/*.md" | ForEach-Object {
    Process-DocFile $_.FullName "cli"
}

# Process API files
Write-Host "`nProcessing API files..."
Get-ChildItem "docs/reference/api/*.md" | ForEach-Object {
    Process-DocFile $_.FullName "api"
}

# Process Features files
Write-Host "`nProcessing Features files..."
Get-ChildItem "docs/concepts/features/*.md" | ForEach-Object {
    Process-DocFile $_.FullName "features"
}

# Process new Tutorial files (skip existing ones with frontmatter)
Write-Host "`nProcessing Tutorial files..."
Get-ChildItem "docs/tutorials/*.md" | ForEach-Object {
    Process-DocFile $_.FullName "tutorials"
}

Write-Host "`nDone! All files processed."
