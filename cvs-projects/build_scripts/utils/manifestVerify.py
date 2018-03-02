#!/usr/bin/python2


from xml.parsers.xmlproc import utils, xmlval, xmldtd

def validateManifest():
  parser = xmlval.XMLValidator()
  parser.set_error_handler(utils.ErrorPrinter(parser))
  dtd = xmldtd.load_dtd('/mvista/arch/manifest.dtd')
  parser.val.dtd = parser.dtd = parser.ent = dtd
  parser.parse_resource('manifest.xml')
  return

def main():
#  print "You shouldn't be running this script by itself."  
#  print "Import this as a module to your python script"
  validateManifest()

if __name__ == '__main__':
  main()


