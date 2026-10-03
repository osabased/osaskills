param([Parameter(Mandatory=$true)][string]$Manifest, [Parameter(Mandatory=$true)][string]$Out)
# Read selected, source-timed frames with the installed Windows OCR engine.
# OCR text is a retrieval lead, never a verified event or corrected player name.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$manifestPath = (Resolve-Path -LiteralPath $Manifest).Path
$outputPath = [IO.Path]::GetFullPath($Out)
if (Test-Path -LiteralPath $outputPath) { throw 'Use a new output file; existing OCR evidence is preserved' }
$json = [IO.File]::ReadAllText($manifestPath)
if (!$json.TrimStart().StartsWith('[')) { throw 'Manifest must be a JSON array of source-timed frames' }
$items = $json | ConvertFrom-Json
if (@($items).Count -eq 0) { throw 'Manifest contains no frames' }
foreach ($item in $items) {
    foreach ($field in @('source_id', 'timestamp_sec', 'file')) {
        if (!$item.PSObject.Properties[$field]) { throw "Missing frame field: $field" }
    }
    if ($item.source_id -isnot [string] -or [string]::IsNullOrWhiteSpace($item.source_id)) { throw 'source_id must be nonempty text' }
    if ($item.timestamp_sec -isnot [ValueType] -or $item.timestamp_sec -is [bool] -or
        [double]::IsNaN($item.timestamp_sec) -or [double]::IsInfinity($item.timestamp_sec) -or $item.timestamp_sec -lt 0) {
        throw 'timestamp_sec must be a finite, nonnegative source timestamp'
    }
    if ($item.file -isnot [string] -or ![IO.Path]::IsPathRooted($item.file) -or !(Test-Path -LiteralPath $item.file -PathType Leaf)) {
        throw 'Each file must be an existing absolute image path from the frame map'
    }
}
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
$script:asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Wait-WinRT($Operation, [Type]$ResultType) {
    $task = $script:asTask.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    if (!$task.Wait(30000)) { throw 'OCR operation timed out' }
    return $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (!$engine) { throw 'No installed OCR language is available' }
$results = @()
foreach ($item in $items) {
    $path = (Resolve-Path -LiteralPath $item.file).Path
    $file = Wait-WinRT ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
    $stream = Wait-WinRT ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    try {
        $decoder = Wait-WinRT ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        if ($decoder.PixelWidth -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension -or
            $decoder.PixelHeight -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension) {
            throw 'Frame exceeds the OCR image limit; prepare a smaller detail frame or a documented crop'
        }
        $bitmap = Wait-WinRT ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        try {
            $recognized = Wait-WinRT ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
            $lines = @($recognized.Lines | ForEach-Object {
                [pscustomobject]@{ text=$_.Text; words=@($_.Words | ForEach-Object {
                    [pscustomobject]@{ text=$_.Text; x=$_.BoundingRect.X; y=$_.BoundingRect.Y;
                        width=$_.BoundingRect.Width; height=$_.BoundingRect.Height }
                }) }
            })
            $results += [pscustomobject]@{ source_id=$item.source_id; timestamp_sec=$item.timestamp_sec; file=$path;
                image_sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant();
                width=$decoder.PixelWidth; height=$decoder.PixelHeight; text=$recognized.Text; lines=$lines }
        } finally { $bitmap.Dispose() }
    } finally { $stream.Dispose() }
}
$report = [pscustomobject]@{
    schema='vod-frame-ocr/v1'; engine='Windows.Media.Ocr'; language=$engine.RecognizerLanguage.LanguageTag;
    manifest=$manifestPath; manifest_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant();
    limitations='Raw OCR may misread names and notices. Check the image before making factual claims. Missing text does not prove an event is absent. Not included in the speech search index.';
    frames=$results
}
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath)) | Out-Null
[IO.File]::WriteAllText($outputPath, ($report | ConvertTo-Json -Depth 12), (New-Object Text.UTF8Encoding($false)))
[pscustomobject]@{ frames=$results.Count; language=$engine.RecognizerLanguage.LanguageTag; report=$outputPath } | ConvertTo-Json
