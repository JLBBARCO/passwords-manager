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

  test do
    assert_predicate bin/"passwords-manager", :exist?
  end
end
