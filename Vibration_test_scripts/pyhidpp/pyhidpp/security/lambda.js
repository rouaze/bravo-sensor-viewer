import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

const client = new S3Client({});

function parseINIString(data) {
  var regex = {
    section: /^\s*\[\s*([^\]]*)\s*\]\s*$/,
    param: /^\s*([^=]+?)\s*=\s*(.*?)\s*$/,
    comment: /^\s*;.*$/,
  };
  var value = {};
  var lines = data.split(/[\r\n]+/);
  var section = null;
  lines.forEach(function (line) {
    if (regex.comment.test(line)) {
      return;
    } else if (regex.param.test(line)) {
      var match = line.match(regex.param);
      if (section) {
        value[section][match[1]] = match[2];
      } else {
        value[match[1]] = match[2];
      }
    } else if (regex.section.test(line)) {
      var match = line.match(regex.section);
      value[match[1]] = {};
      section = match[1];
    } else if (line.length == 0 && section) {
      section = null;
    }
  });
  return value;
}

export const handler = async (event, context) => {
  var body = "";
  var statusCode = "200";
  if (event.queryStringParameters && event.queryStringParameters.fw) {
    const requestedFw = event.queryStringParameters.fw;
    const command = new GetObjectCommand({
      Bucket: "x1602-enc-mecha",
      Key: "passwords_enc_mecha.ini",
    });

    try {
      const response = await client.send(command);
      // The Body object also has 'transformToByteArray' and 'transformToWebStream' methods.
      const str = await response.Body.transformToString();
      const keys = parseINIString(str);
      if (requestedFw in keys) {
        body = keys[requestedFw]["x1E02_Manuf"];
      } else {
        statusCode = "404"
        body = "FW key not found";
      }
    } catch (err) {
      console.error(err);
    }
  } else {
    statusCode = "400"
    body = "Unspecified request";

  }
  /*
   * Generate HTTP response using 200 status code with a simple body.
   */
  const response = {
    statusCode: statusCode,
    // statusDescription: 'OK',
    headers: {},
    body: body,
  };

  return response;
};
