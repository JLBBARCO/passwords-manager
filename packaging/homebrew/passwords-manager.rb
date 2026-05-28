class PasswordsManager < Formula
  desc "Password manager with encrypted local storage"
  homepage "https://github.com/JLBBARCO/passwords-manager"
  version "0.0.0"

  on_macos do
    url "https://github.com/JLBBARCO/passwords-manager/releases/download/v#{version}/passwords-manager-macos.tar.gz"
    sha256 "REPLACE_WITH_MACOS_SHA256"
  end

  on_linux do
    url "https://github.com/JLBBARCO/passwords-manager/releases/download/v#{version}/passwords-manager-linux.tar.gz"
    sha256 "REPLACE_WITH_LINUX_SHA256"
  end

  def install
    bin.install "passwords-manager"
    prefix.install "README.md" if File.exist?("README.md")
    prefix.install "LICENSE" if File.exist?("LICENSE")
  end

  def post_install
    home_dir = ENV["HOME"]
    return if home_dir.to_s.empty?

    if OS.linux?
      app_dir = Pathname.new(home_dir) / ".local/share/applications"
      app_dir.mkpath

      (app_dir / "passwords-manager.desktop").write <<~EOS
        [Desktop Entry]
        Type=Application
        Version=1.0
        Name=Passwords Manager
        Exec=#{opt_bin}/passwords-manager
        Terminal=false
        Categories=Utility;Security;
      EOS
    elsif OS.mac?
      app_dir = Pathname.new(home_dir) / "Applications"
      app_dir.mkpath

      launcher = app_dir / "Passwords Manager.command"
      launcher.write <<~EOS
        #!/bin/bash
        "#{opt_bin}/passwords-manager"
      EOS
      launcher.chmod(0755)
    end
  end

  test do
    assert_predicate bin/"passwords-manager", :exist?
  end
end
