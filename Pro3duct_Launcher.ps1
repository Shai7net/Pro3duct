param([switch]$ValidateOnly)

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Decode-Hebrew([string]$Value) {
    return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Value))
}

$T = @{
    AppSubtitle = Decode-Hebrew "157Xm9eZ158g15DXqiDXodeR15nXkdeqINeZ16bXmdeo16og15TXnteV15PXnNeZ150g16nXnNea"
    Starting = Decode-Hebrew "157XqteX15nXnC4uLg=="
    FirstRun = Decode-Hebrew "15TXqteU15zXmdeaINei16nXldeZINec16fXl9eqINee16LXmCDXltee158g15HXlNek16LXnNeUINeU16jXkNep15XXoNeU"
    KeepOpen = Decode-Hebrew "16DXkCDXnNeU16nXkNeZ16gg15fXnNeV158g15bXlCDXpNeq15XXlyDXoteTINep15TXmdeZ16nXldedINei15XXnNeU"
    CannotOpen = Decode-Hebrew "15zXkCDXoNeZ16rXnyDXnNek16rXldeXINeQ16ogUHJvM2R1Y3Q="
    CheckingEnv = Decode-Hebrew "15HXldeT16cg15DXqiDXodeR15nXkdeqINeU15TXpNei15zXlA=="
    CheckingDocker = Decode-Hebrew "157XldeV15PXkCDXqS1Eb2NrZXIg15bXnteZ158="
    DockerMissing = Decode-Hebrew "RG9ja2VyIERlc2t0b3Ag15DXmdeg15Ug157Xldeq16fXnyDXkdee15fXqdeRLiDXmdepINec15TXqten15nXnyDXkNeV16rXlSDXnNek16DXmSDXlNek16LXnNeqINeU15nXmdep15XXnS4="
    StartingDocker = Decode-Hebrew "157XpNei15nXnCDXkNeqIERvY2tlciBEZXNrdG9w"
    WaitingDocker = Decode-Hebrew "157Xnteq15nXnyDXqdee16DXldeiINeU15TXpNei15zXlCDXmdeU15nXlCDXnteV15vXnw=="
    DockerLocation = Decode-Hebrew "RG9ja2VyIERlc2t0b3Ag15zXkCDXoNee16bXkCDXkdee15nXp9eV150g15TXptek15XXmS4="
    DockerTimeout = Decode-Hebrew "RG9ja2VyIERlc2t0b3Ag15zXkCDXlNem15zXmdeXINec16LXnNeV16og15HXltee158uINeg16HXlCDXnNek16rXldeXINeQ15XXqteVINeZ15PXoNeZ16og15XXkNeWINec15TXpNei15nXnCDXqdeV15Eg15DXqiBQcm8zZHVjdC4="
    CheckCount = Decode-Hebrew "15HXk9eZ16fXlCB7MH0g157XqteV15ogOTA="
    StartingServices = Decode-Hebrew "157Xotec15Qg15DXqiDXqdeZ16jXldeq15kgUHJvM2R1Y3Q="
    LoadingServices = Decode-Hebrew "15jXldei158g15DXqiDXlNep16jXqiwg157XodeTINeU16DXqteV16DXmdedINeV16LXldeo15og15TXqtec16ot157XnteT"
    PreparingComponents = Decode-Hebrew "15TXntei16jXm9eqINee15vXmdeg15Qg15DXqiDXm9ecINeU16jXm9eZ15HXmdedINeU15PXqNeV16nXmded"
    ComposeFailed = Decode-Hebrew "15TXpNei15zXqiDXqdeZ16jXldeq15kgUHJvM2R1Y3Qg16DXm9ep15zXlC4g15DXpNep16gg15zXkdeT15XXpyDXkNeqIERvY2tlciBEZXNrdG9wINeV15zXoNeh15XXqiDXqdeV15Eu"
    AlmostReady = Decode-Hebrew "15vXntei15gg157Xldeb158="
    WaitingApp = Decode-Hebrew "157Xnteq15nXnyDXqdeU16nXqNeqINeV15TXntee16nXpyDXmdeU15nXlSDXltee15nXoNeZ150="
    CheckingLoaded = Decode-Hebrew "15HXldeT16cg16nXm9ecINeo15vXmdeR15kg15TXmdeZ16nXldedINeg15jXoteg15U="
    AppTimeout = Decode-Hebrew "15TXqdeZ16jXldeq15nXnSDXotec15UsINeQ15HXnCDXlNee157XqdenINei15PXmdeZ158g15DXmdeg15Ug15bXnteZ158uINeg16HXlCDXnNeU16TXoteZ15wg16nXldeRINeR16LXldeTINeo15LXoi4="
    EdgeMissing = Decode-Hebrew "TWljcm9zb2Z0IEVkZ2Ug15DXmdeg15Ug157Xldeq16fXny4g15TXldeQINeT16jXldepINec16TXqteZ15fXqiDXl9ec15XXnyDXlNeZ15nXqdeV150g15TXotem157XkNeZLg=="
    AllReady = Decode-Hebrew "15TXm9eV15wg157Xldeb158="
    OpeningApp = Decode-Hebrew "16TXldeq15cg15DXqiBQcm8zZHVjdA=="
}

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" Title="Pro3duct" Width="620" Height="390" WindowStartupLocation="CenterScreen" WindowStyle="None" ResizeMode="NoResize" Background="#080810" AllowsTransparency="True" Topmost="True" FlowDirection="RightToLeft">
  <Border CornerRadius="22" BorderBrush="#3A315E" BorderThickness="1" Background="#101124" Padding="38">
    <Grid>
      <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="*"/><RowDefinition Height="Auto"/></Grid.RowDefinitions>
      <StackPanel Grid.Row="0" HorizontalAlignment="Center">
        <Border Width="72" Height="72" CornerRadius="20" Background="#8B5CF6" HorizontalAlignment="Center"><TextBlock Text="P3" Foreground="White" FontSize="27" FontWeight="Bold" HorizontalAlignment="Center" VerticalAlignment="Center" FlowDirection="LeftToRight"/></Border>
        <TextBlock Text="Pro3duct" Foreground="White" FontSize="32" FontWeight="Bold" HorizontalAlignment="Center" Margin="0,18,0,0" FlowDirection="LeftToRight"/>
        <TextBlock Text="$($T.AppSubtitle)" Foreground="#A9A7BC" FontSize="16" HorizontalAlignment="Center" Margin="0,8,0,0"/>
      </StackPanel>
      <StackPanel Grid.Row="1" VerticalAlignment="Center">
        <TextBlock Name="StatusText" Text="$($T.Starting)" Foreground="#F3F4F6" FontSize="17" FontWeight="SemiBold" HorizontalAlignment="Center" TextAlignment="Center"/>
        <TextBlock Name="DetailText" Text="$($T.FirstRun)" Foreground="#8D8BA0" FontSize="13" HorizontalAlignment="Center" TextAlignment="Center" Margin="0,8,0,22"/>
        <ProgressBar Name="Progress" Height="10" Minimum="0" Maximum="100" Value="5" Foreground="#8B5CF6" Background="#25263A" BorderThickness="0"/>
      </StackPanel>
      <TextBlock Grid.Row="2" Text="$($T.KeepOpen)" Foreground="#6F6D82" FontSize="12" HorizontalAlignment="Center"/>
    </Grid>
  </Border>
</Window>
"@

$reader = New-Object System.Xml.XmlNodeReader ([xml]$xaml)
$window = [Windows.Markup.XamlReader]::Load($reader)
$statusText = $window.FindName("StatusText")
$detailText = $window.FindName("DetailText")
$progress = $window.FindName("Progress")

if ($ValidateOnly) {
    if (-not $statusText -or -not $detailText -or -not $progress -or -not $T.AppSubtitle) {
        throw "Launcher validation failed"
    }
    Write-Output "Launcher validation OK"
    exit 0
}

function Update-Splash([string]$Status, [string]$Detail, [int]$Value) {
    $statusText.Text = $Status
    $detailText.Text = $Detail
    $progress.Value = $Value
    $window.Dispatcher.Invoke([action]{}, [System.Windows.Threading.DispatcherPriority]::Background)
}

function Test-Docker {
    try {
        & docker info --format "{{.ServerVersion}}" 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-Url([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Fail-Launch([string]$Message) {
    Update-Splash $T.CannotOpen $Message 100
    Start-Sleep -Seconds 3
    $window.Close()
    [System.Windows.MessageBox]::Show($Message, "Pro3duct", "OK", "Error") | Out-Null
    exit 1
}

$window.Show()
Update-Splash $T.CheckingEnv $T.CheckingDocker 10

$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCommand) {
    Fail-Launch $T.DockerMissing
}

$dockerReady = Test-Docker
if (-not $dockerReady) {
    $dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path $dockerDesktop)) {
        Fail-Launch $T.DockerLocation
    }
    Update-Splash $T.StartingDocker $T.WaitingDocker 20
    Start-Process -FilePath $dockerDesktop -WindowStyle Hidden
    for ($i = 1; $i -le 90; $i++) {
        $dockerReady = Test-Docker
        if ($dockerReady) { break }
        Update-Splash $T.StartingDocker ($T.CheckCount -f $i) ([Math]::Min(42, 20 + [Math]::Floor($i / 4)))
        Start-Sleep -Seconds 2
    }
    if (-not $dockerReady) { Fail-Launch $T.DockerTimeout }
}

Update-Splash $T.StartingServices $T.LoadingServices 48
$compose = Start-Process -FilePath $dockerCommand.Source -ArgumentList @("compose", "up", "-d", "--build") -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
while (-not $compose.HasExited) {
    Update-Splash $T.StartingServices $T.PreparingComponents ([Math]::Min(78, $progress.Value + 1))
    Start-Sleep -Milliseconds 900
}
if ($compose.ExitCode -ne 0) { Fail-Launch $T.ComposeFailed }

Update-Splash $T.AlmostReady $T.WaitingApp 82
$appReady = $false
for ($i = 1; $i -le 60; $i++) {
    $apiReady = Test-Url "http://localhost:8000/api/v1/health"
    $frontendReady = Test-Url "http://localhost:3000/dashboard"
    if ($apiReady -and $frontendReady) { $appReady = $true; break }
    Update-Splash $T.AlmostReady $T.CheckingLoaded ([Math]::Min(96, 82 + [Math]::Floor($i / 4)))
    Start-Sleep -Seconds 1
}
if (-not $appReady) { Fail-Launch $T.AppTimeout }

$edgePaths = @("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "C:\Program Files\Microsoft\Edge\Application\msedge.exe")
$edge = $edgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { Fail-Launch $T.EdgeMissing }

Update-Splash $T.AllReady $T.OpeningApp 100
Start-Sleep -Milliseconds 650
$window.Close()

$profilePath = Join-Path $ProjectRoot ".pro3duct-app-profile"
Start-Process -FilePath $edge -ArgumentList @("--app=http://localhost:3000/dashboard", "--start-maximized", "--no-first-run", "--disable-features=msEdgeSidebarV2", "--user-data-dir=$profilePath")
