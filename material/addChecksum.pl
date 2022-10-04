#!/usr/bin/perl

#############################################################################
#                                                                           #
#     This is a script to add checksums to a subscription file.             #
#     Run the script like this:                                             #
#                                                                           #
#       perl addChecksum.pl subscription.txt                                #
#                                                                           #
#     Note: The subscription file should be saved in UTF-8 encoding.        #
#                                                                           #
#############################################################################

use strict;
use warnings;
use Digest::MD5 qw(md5_base64);

die "Usage: $^X $0 subscription.txt\n" unless @ARGV;

my $file = $ARGV[0];
my $content = readFile($file);

# Remove existing checksum
$content =~ s/^.*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n//gmi;

# Load the subscription content
my $checksumData = $content;

# Remove all CR symbols and empty lines
$checksumData =~ s/\r//g;
$checksumData =~ s/\n+/\n/g;

# Calculate new checksum
my $checksum = md5_base64($checksumData);

# Insert new checksum into the second line of the file
$content =~ s/(\r?\n)/$1! Checksum: $checksum$1/;

writeFile($file, $content);
print "Added Checksum for $file\n";

sub readFile
{
  my $file = shift;

  open(local *FILE, "<", $file) || die "Could not read file '$file'";
  binmode(FILE);
  local $/;
  my $result = <FILE>;
  close(FILE);

  return $result;
}

sub writeFile
{
  my ($file, $contents) = @_;

  open(local *FILE, ">", $file) || die "Could not write file '$file'";
  binmode(FILE);
  print FILE $contents;
  close(FILE);
}

